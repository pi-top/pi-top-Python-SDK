# Pitop SDK Images

The images here have been adjusted for programatic use, primarily in the
'Simulatable' mixin for creating virtual representations of the components.

## General
The starting point for setting the dimensions of these images was having the
pi-top 4 miniscreen represented at it's real 128x64 pixel size, and keeping the
rest of the components to scale with this.

This results in an approximate scale factor for image to real world dimensions
of **4.265 pixels per millimeter** (128px/30mm).

The component images are cropped to remove any background and borders and then
scaled relative to their real-life dimensions.

## Components
### Pitop
#### Image dimensions
Width: 435px
Height: 573px

Miniscreen Edges (x1, y1, x2, y2): 152, 340, 280, 404

#### Physical dimensions
Pitop width: 105mm
Pitop height: 131mm
Miniscreen width: 30mm (sf 4.266 ppmm)
Miniscreen height: 15mm (sf 4.266 ppmm)

### PMA cubes
Width: 102px
Height: 102px
#### Physical Dimensions
Width: 24mm (sf 4.25)
Height: 24mm (sf 4.25)

## Process
To produce these images, the existing renders from /docs were processed with
imagemagick and paint.net. Some examples given here:

### Background removal
`convert Pitop-original.jpg -fuzz 16% -fill none -draw "color 1,1 floodfill"
Pitop.png`
`convert led_green.jpg -fuzz 80% -fill none -draw "color 1,1 floodfill"
LED_green.png`

### Cropping & resizing
Cropping to the edge of the non-transparent pixels done in paint.net.

Images then resized based on measurements of physical hardware at 4.265 pixels
per millimeter scale, rounded to nearest pixel. This was done in paint.net or
with `convert -resize`

### Final processing
To produce variants such as LEDS in 'on' and 'off' states the saturation was
adjusted:
`convert LED_green.jpg -modulate 100,50 LED_green_off.png`
`convert LED_green.jpg -modulate 100,200 LED_green_on.png`
