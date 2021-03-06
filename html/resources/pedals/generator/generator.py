#!/usr/bin/env python

# This generator takes a special GIMP file and generates different
# PNG images from it.
# The source must contain some hidden layers with a special prefix in
# their name. The script loops over those layers taking the following
# actions:
#     * layer is set to visible
#     * all visible layers are merged
#     * the result together with two (hidden) b/w masks are copied to new image
#     * the result gets resized the following way (e.g. horizontal):
#         * the base layer is copied and a mask is applied
#         * the base layer gets cropped by the necessary amount of pixels
#           plus borderx from the right
#         * the masked copy is translated by the necessary amount of pixels
#           to the left
#         * the masked copy is merged onto the base layer
#         * the masks are deleted
#         * the image is exported to its final destination as PNG

import os
import sys
import imp
import getopt
import gimp


def css (mod):
    O = mod.options
    with open (O["css_source"], "r") as css_file:
        css_in=css_file.read()
    bg_str = ""
    for c in mod.colors:
        bg_str += mod.backgrounds_css.replace("<COLOR>", c)
    css_out = css_in.replace("<BACKGROUNDS>", bg_str);
    col_str = ""
    for cs in mod.colors_css:
        cols = { }
        for c in mod.colors:
            if not mod.colors[c] in cs:
                continue
            if not mod.colors[c] in cols:
                cols[mod.colors[c]] = [ ];
            cols[mod.colors[c]] += [ cs["identifier"].replace("<COLOR>", c) ]
        for c in cols:
            col_str += ",\n".join(cols[c]) + "\n"
            col_str += cs[c] + "\n"
    with open(O["css_dest"], "w") as out_file:
        out_file.write(css_out.replace("<COLORS>", col_str))
    
def images (mod):
    O = mod.options
    cols = mod.colors.keys()
    for c in mod.colors.keys():
        p = os.path.join(O["chdir"], mod.sizes[0]['folder'], "%s%s" % (c, O["export_suffix"]))
        if not force and os.path.isfile(p):
            cols.remove(c);
    if not len(cols):
        print "Nothing to do."
        return
    O["colors"] = "\"" + "\" \"".join(cols) + "\""
    O["sizes"] = ""
    for s in range(0, len(mod.sizes)):
        O["sizes"] += "\n(list (list %d %d) \"%s%s/\")" % (mod.sizes[s]["x"], mod.sizes[s]["y"], mod.options["chdir"], mod.sizes[s]["folder"])
    exe = gimp.colors
    for r in O:
        exe = exe.replace("<" + r.upper() + ">", str(O[r]))
    os.system(exe)
    
def usage():
    print """Generator for backgrounds and CSS files of MOD stomp boxes.

USAGE:
    generator.py {-c | --css} {-i | --images} {-h | --help} TYPE [TYPE...]

OPTIONS:
    -c --css
        Generate CSS file(s)
    
    -f --force
        Force re-generation of already existing backgrounds
    
    -h --help
        Show this help
        
    -i --images
        Generate background images from GIMP file

EXAMPLE:
    generator.py -c boxy
        Creates the CSS script for all boxy types
    
    generator.py -i -c boxy lata
        Creates CSS and background images for all boxy and lata types"""
        
if __name__ == '__main__':
    try:
        opts, args = getopt.getopt(sys.argv[1:], "cihf", ["css", "images", "help", "force"])
    except getopt.GetoptError as err:
        print str(err)
        usage()
        sys.exit(2)
    _css    = False
    _images = False
    force   = False
    if not len(opts) or not len(args):
        usage()
        exit(0)
    for o, a in opts:
        if o in ("-c", "--css"):
            _css = True
        if o in ("-i", "--images"):
            _images = True
        if o in ("-h", "--help"):
            usage()
            exit(0)
        if o in ("-f", "--force"):
            force = True
    for a in args:
        try:
            mod = imp.load_source(a, os.path.join("configs", "%s.py" % a))
        except:
            print "No module named %s" % a
            continue
        if (_images):
            print "Creating images for %s..." % a
            images(mod)
        if (_css):
            print "Creating CSS for %s..." % a
            css(mod)
