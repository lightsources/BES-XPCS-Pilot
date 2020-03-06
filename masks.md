Contents

- [Masks](#masks)
  - [Boolean mask](#boolean-mask)
  - [Descriptive boolean mask](#descriptive-boolean-mask)
  - [Region of Interest](#region-of-interest)
    - [Selective array mask](#selective-array-mask)
    - [cumulative array mask](#cumulative-array-mask)
      - [example: logical OR](#example-logical-or)
      - [example: logical AND](#example-logical-and)
  - [mask described by parameters](#mask-described-by-parameters)

# Masks

A mask is used as a filter, to mark 
pixels of an image (array)
for special consideration during data 
handling or visualization.
The concept of a mask is useful when 
the actual removal of the
masked data would alter the image 
(such as removal of pixel(s) from an
array would change its shape).

*Note: **shape** refers to the rank and dimensions of 
an array.  The rank is the number of indices and 
the dimensions are the number of values in each 
index.  An array with shape (2,3) has rank=2, 
and has 2 rows and 3 columns.*


In its simplest form, a mask is used to identify 
pixels which should not be used.  A mask is often 
described by an array of the same shape (same numbers 
of rows and columns) as the image.
Alternatively, a mask may be described by procedure 
(such as *divide this rectangle into four
equal-size regions*).

To illustrate, we first create an image array (this one is a 4x4 array
of random numbers between 0 and 255):

```
26	29	212	24
72	116	27	104
212	184	146	49
102	222	27	77
```

## Boolean mask

Consider this example of a simple keep/discard 
mask, represented by boolean
values (where a zero means keep this pixel and a one 
means discard this pixel).  The boolean mask array is 
the same shape as the image array.

Mask *out* (remove) the pixels in the upper left quadrant:

```
1	1	0	0
1	1	0	0
0	0	0	0
0	0	0	0
```

Apply the mask to the image.  (Here, a `-` shows that 
the pixel will be ignored.):

```
-	-	212	24
-	-	27	104
212	184	146	49
102	222	27	77
```

## Descriptive boolean mask

In some cases, it is desired to retain information that describes
*why* a pixel will be masked.  One example is the 
[NeXus](https://www.nexusformat.org/)
[`pixel_mask`](https://manual.nexusformat.org/classes/base_classes/NXdetector.html#index-59).  The 
`pixel_mask` works the same way as the boolean mask:
means keep this pixel and *non-zero* means 
discard this pixel.  The descriptive boolean mask array 
is the same shape as the image array.
The value of each pixel in the mask is a
[bit map](https://en.wikipedia.org/wiki/Bitmap) where 
each bit has a certain meaning (pixel is: dead, noisy, 
over responding, no sensor, ...).  Since this is a 
bit mask, multiple meanings may be added together.

As an example, let's define a `pixel_mask` that excludes the corner pixels with bit 0 (as if there is no sensor), a noisy pixel with 4, and one dead pixel with bit 1.

```
1	0	0	1
0	2	0	0
16	0	0	0
1	0	0	1
```

We then apply the `pixel_mask` to the `image` above (using this spreadsheet calculation: `=IF(mask_pixel=0,image_pixel,"-")`):

```
-	29	212	-
72	-	27	104
-	184	146	49
-	222	27	-
```


## Region of Interest

Another common type of mask that differs from the 
boolean mask is a region (or regions) of interest (ROI)
within the image to be kept, discarding all pixels
not included in the ROI.  A ROI may be associated 
with an additional parameter,
such as elemental mapping, crystal orientation, 
or *Q* vector magnitude.

### Selective array mask

A *selective array mask* assigns meanings to various pixels
in the image.  Each value in the mask assigns that pixel
to a specific meaning.  (This is the same as an indexed 
map of the ROIs.)  The value is the index number of 
the associated meaning.  The selective array mask is the 
same shape as the image array.

Let's illustrate with the `image` above, assigning
each of the four quadrants to a different ROI 
and also assigning the center 4 pixels to a different ROI.
We'll start the ROI numbering at zero.  

The *ROI_names* of our contrived example are:

index | ROI name
:---: | :---
0 | ignore
1 | upper-left
2 | lower-left
3 | lower-right
4 | upper-right

*Hint: Write these names into a string array in the data file.*

Here is the selective mask array that describes these ROIs:

```
1	1	4	4
1	0	0	4
2	0	0	3
2	2	3	3
```

These are the 5 ROIs that result when the selective mask array is applied to the `image` above:


```
ROI	0		
-	-	-	-
-	116	27	-
-	184	146	-
-	-	-	-
			
ROI	1		
26	29	-	-
72	-	-	-
-	-	-	-
-	-	-	-
			
ROI	2		
-	-	-	-
-	-	-	-
212	-	-	-
102	222	-	-
			
ROI	3		
-	-	-	-
-	-	-	-
-	-	-	49
-	-	27	77
			
ROI	4		
-	-	212	24
-	-	-	104
-	-	-	-
-	-	-	-
```

### cumulative array mask

A descriptive boolean mask is a composite of several types
of mask.  Alternative to the use of a bit mask, the mask
could result from the combination of various component
boolean masks, either using logical OR 
or logical AND operations.

In this case, the mask array object has rank that is 
one greater than the rank of the image array.  The 
additional index is the number of component boolean 
masks.  Each of these component masks has the same 
shape as the `image`.

#### example: logical OR

To generate the same mask as the 
[Descriptive boolean mask](#descriptive-boolean-mask) 
above,

```
1	0	0	1
0	2	0	0
16	0	0	0
1	0	0	1
```

we need three component masks which will be combined
with a logical OR:

This masks the corners:

```
1	0	0	1
0	0	0	0
0	0	0	0
1	0	0	1
```

This is the dead pixel:

```
0	0	0	0
0	2	0	0
0	0	0	0
0	0	0	0
```

This is the noisy pixel:

```
0	0	0	0
0	0	0	0
16	0	0	0
0	0	0	0
```

BUT, since these are now boolean masks, and so
will be the resulting combined mask, this mask array 
has shape (3, 4, 4) with values (0=keep pixel, 
1=mask pixel:

```
1	0	0	1
0	0	0	0
0	0	0	0
1	0	0	1

0	0	0	0
0	1	0	0
0	0	0	0
0	0	0	0

0	0	0	0
0	0	0	0
1	0	0	0
0	0	0	0
```

When these are combined with a logical OR, this is
the computed mask:

```
1	0	0	1
0	1	0	0
1	0	0	0
1	0	0	1
```

which is then handled as a boolean mask.

#### example: logical AND

TODO:

## mask described by parameters

TODO:
