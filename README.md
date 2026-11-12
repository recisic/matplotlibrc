## My matplotlib preset
> *Flavored with [Lato fonts](https://www.latofonts.com) and [tailwindcss](https://tailwindcss.com) color palette*

### Installation on Linux
1. Copy the ttf files in `fonts/` to the `~/.local/share/fonts/` directory and run `fc-cache -fv ~/.local/share/fonts/` to update the font cache.
2. To use as the default matplotlib style, copy the `matplotlibrc` file to your `~/.config/matplotlib/` directory.
3. If matplotlib does not pick up the new fonts, delete its font cache (`~/.cache/matplotlib/fontlist-*.json`).

The fonts are Late Sans: [Lato](https://www.latofonts.com) 2.015 with the math symbols Lato lacks (∇, ∝, ⋅, ⟨ ⟩) added from [Lete Sans Math](https://github.com/abccsss/LeteSansMath), under a new name as Lato's license requires. `fonts/build_late_sans.py` rebuilds them from the original fonts.

For other options, please refer to the [official documentation](https://matplotlib.org/stable/users/explain/customizing.html).

### Example figure
<div align="center">
<img src="assets/example.png" alt="example figure" width="400"/>
</div>

You may need to configure the marker sizes, line widths, etc. to fit your needs.

### More colors
See the [tailwindcss color palette](https://tailwindcss.com/docs/customizing-colors) for colorful inspiration!
