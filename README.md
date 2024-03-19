# AIPaintingSupportProgram
Require python &gt; 3.10


Tool box for SDWebUI

**1. Resize**

Resize the image in selected folder

Param 1, 3: Target size
Param 4: Result image type

Param 3 Seperate Vertical: Divide this image into X equal-sized horizontal sections

**2. Watermark**

Add watermark in all the image in the selected folder

Ratio: the size of image for watermark
Position: the start x,y (from 0~1) in the target image for the watermark to put on

**3. Editor**

Unused now

**4. Mosaic**

Add mosaic on the image in the selected folder

Select ROI Shrink ratio : shrink the image for adding mosaic

Mosaic pixel size: Pixel size of mosaic (-1 for 0.01 * short side)

In this mode

Press a to change to previous image, d to change to next image
Press r to revert last line
Press space key to return to original image size * shrink ratio
Press s to process mosaic
Press ESC to exit

Draw a cross to mosaic the area of the cross

**5. Text Transform**

  1. Transform CivitAI : Change all the text into lower case (If copy from the trigger word)
                        For example : (1GIRL SOLO) will be convert to 1girl, solo
  2. Remove strength : Remove the strength in webUI format
  3. NAI to webUI : Convert the strength from NAI format to webUI format
  4. Booru to WebUI : Convert the Tag in booru to WebUI format

**5. Lora XY Plot**

Generate string for XY plot to test lora

For example, select a folder contain LoraA.safetensor and LoraB.safetensor

Weight set to 0.5, 1.0

It will generate &lt;lora:LoraA:0.3&gt;, &lt;lora:LoraA:0.5&gt;, &lt;lora:LoraA:0.7&gt;, &lt;lora:LoraA:1.0&gt;, &lt;lora:LoraB:0.3&gt;, &lt;lora:LoraB:0.5&gt;, &lt;lora:LoraB:0.7&gt;, &lt;lora:LoraB:1.0&gt;
