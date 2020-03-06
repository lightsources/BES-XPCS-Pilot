# Masks

A mask is used as a filter, to mark pixels of an image (array)
for special consideration during data handling or visualization.
The concept of a mask is useful when the actual removal of the
masked data would alter the image (such as removal of pixel(s) from an
array would change its shape).

In its simplest form, a mask is used to identify pixels which 
should not be used.  A mask is often described by an array of 
the same shape (same numbers of rows and columns) as the image.
Alternatively, a mask may be described by procedure (such as
*divide this rectangle into four equal-size regions*).

## Boolean mask

Consider this example of a simple keep/discard mask, represented by boolean
values (where a zero means keep this pixel and a one means 
discard this pixel).  First, take an image (this one is a 4x4 array
of random numbers between 0 and 255):

```
 26  29 212  24
 72 116  27 104
212 184 146  49
102 222  27  77
```

Mask *out* (remove these pixels) the upper left quadrant:

```
1 1 0 0
1 1 0 0
0 0 0 0
0 0 0 0
```

Apply the mask to the image.  (Here, a `-` shows that 
the pixel will be ignored.):

```
 -   -  212  24
 -   -   27 104
212 184 146  49
102 222  27  77
```

## Descriptive boolean mask

In some cases, it is desired to retain information that describes
*why* a pixel will be masked.  One example is the 
[NeXus](https://www.nexusformat.org/)
[`pixel_mask`](https://manual.nexusformat.org/classes/base_classes/NXdetector.html#index-59).  The `pixel_mask` works the same way as the boolean mask:
means keep this pixel and *non-zero* means 
discard this pixel.  The value of each pixel in the mask is a
[bit map](https://en.wikipedia.org/wiki/Bitmap) where each bit is
describes a certain meaning (pixel is: dead, noisy, over responding, 
no sensor, ...).

## Region of Interest

Another common case that differs from the boolean mask 
is to identify a region (or regions) of interest (ROI)
within the image to be kept, discarding all pixels
not included in the ROI.  
A ROI may be associated with an additional parameter,
such as elemental mapping or *Q* vector magnitude.

```
TODO: more work needed here

two ways: 

1. one mask array with values that are region indices
2. *n* mask arrays, each as boolean masks

Way 1 is for non-overlapping ROIs, while way 2 allows for the 
possibility that a pixel may be included in more than one ROI.
```
