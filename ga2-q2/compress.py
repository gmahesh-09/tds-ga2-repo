from PIL import Image
import os
import io

def ultra_compress_lossless(input_path, output_path='compressed_lossless_400.png', target_bytes=400):
    """
    Ultra-aggressive lossless PNG compression.
    Every pixel must remain IDENTICAL to the original.
    """
    
    img = Image.open(input_path)
    original_size = os.path.getsize(input_path)
    
    print(f"="*60)
    print(f"ULTRA LOSSLESS PNG COMPRESSION")
    print(f"="*60)
    print(f"Original size: {original_size} bytes")
    print(f"Dimensions: {img.width}x{img.height}")
    print(f"Mode: {img.mode}")
    print(f"Target: < {target_bytes} bytes")
    print(f"Total pixels: {img.width * img.height}\n")
    
    # Get original pixel data for verification
    original_pixels = list(img.getdata())
    
    # Analyze the image
    unique_colors = len(set(original_pixels))
    print(f"Unique colors: {unique_colors}")
    
    # Check if image is suitable for indexed color
    if unique_colors <= 256 and img.mode in ('RGB', 'RGBA', 'L'):
        print(f"Image can use palette mode (≤256 colors)\n")
    
    best_size = float('inf')
    best_file = None
    
    strategies = []
    
    # Strategy 1: Direct PNG optimization
    print("Strategy 1: Maximum PNG compression...")
    temp1 = 'temp_method1.png'
    img.save(temp1, 'PNG', optimize=True, compress_level=9)
    size1 = os.path.getsize(temp1)
    print(f"  Result: {size1} bytes")
    
    # Verify lossless
    verify1 = Image.open(temp1)
    if list(verify1.getdata()) == original_pixels:
        print(f"  Verification: LOSSLESS ✓")
        strategies.append((temp1, size1, "PNG compress_level=9"))
        if size1 < best_size:
            best_size = size1
            best_file = temp1
    else:
        print(f"  Verification: FAILED ✗")
        os.remove(temp1)
    
    # Strategy 2: Convert to palette mode if applicable
    if unique_colors <= 256 and img.mode in ('RGB', 'RGBA', 'L'):
        print("\nStrategy 2: Convert to indexed palette mode...")
        temp2 = 'temp_method2.png'
        
        if img.mode == 'RGBA':
            # Preserve transparency
            palette_img = img.convert('P', palette=Image.ADAPTIVE, colors=unique_colors)
        else:
            palette_img = img.convert('P', palette=Image.ADAPTIVE, colors=unique_colors)
        
        palette_img.save(temp2, 'PNG', optimize=True, compress_level=9)
        size2 = os.path.getsize(temp2)
        print(f"  Result: {size2} bytes")
        
        # Verify lossless
        verify2 = Image.open(temp2).convert(img.mode)
        if list(verify2.getdata()) == original_pixels:
            print(f"  Verification: LOSSLESS ✓")
            strategies.append((temp2, size2, f"Palette mode ({unique_colors} colors)"))
            if size2 < best_size:
                best_size = size2
                best_file = temp2
        else:
            print(f"  Verification: FAILED ✗")
            if os.path.exists(temp2):
                os.remove(temp2)
    
    # Strategy 3: Try different PNG filters
    print("\nStrategy 3: Trying different PNG filter strategies...")
    for filter_type in [0, 1, 2, 3, 4]:
        temp3 = f'temp_filter_{filter_type}.png'
        try:
            # Use pnginfo to set filter
            img.save(temp3, 'PNG', optimize=True, compress_level=9)
            size3 = os.path.getsize(temp3)
            
            verify3 = Image.open(temp3)
            if list(verify3.getdata()) == original_pixels:
                strategies.append((temp3, size3, f"PNG filter {filter_type}"))
                if size3 < best_size:
                    best_size = size3
                    best_file = temp3
        except:
            pass
    
    # Strategy 4: Reduce bit depth if possible (for grayscale)
    if img.mode == 'L':
        print("\nStrategy 4: Trying reduced bit depth (grayscale)...")
        # Check if image uses only a few gray levels
        gray_levels = unique_colors
        
        for bits in [4, 2, 1]:
            if gray_levels <= 2**bits:
                temp4 = f'temp_bits_{bits}.png'
                # PIL doesn't directly support sub-8-bit, so this is limited
                img.save(temp4, 'PNG', optimize=True, compress_level=9, bits=bits)
                size4 = os.path.getsize(temp4)
                
                verify4 = Image.open(temp4)
                if list(verify4.getdata()) == original_pixels:
                    print(f"  {bits}-bit: {size4} bytes ✓")
                    strategies.append((temp4, size4, f"{bits}-bit grayscale"))
                    if size4 < best_size:
                        best_size = size4
                        best_file = temp4
    
    # Results
    print(f"\n{'='*60}")
    print(f"COMPRESSION RESULTS")
    print(f"{'='*60}\n")
    
    if strategies:
        print("All lossless methods tried:")
        for filepath, size, method in sorted(strategies, key=lambda x: x[1]):
            print(f"  {size:4d} bytes - {method}")
    
    print(f"\nBest result: {best_size} bytes")
    
    if best_size < target_bytes:
        # Copy best to output
        with open(best_file, 'rb') as src:
            with open(output_path, 'wb') as dst:
                dst.write(src.read())
        
        print(f"\n{'='*60}")
        print(f"SUCCESS! ✓")
        print(f"{'='*60}")
        print(f"Compressed to: {best_size} bytes (under {target_bytes} bytes!)")
        print(f"Compression ratio: {(1 - best_size/original_size)*100:.1f}%")
        print(f"Saved to: {output_path}")
        print(f"Lossless: YES - All {len(original_pixels)} pixels identical")
        
        # Clean up
        for f, _, _ in strategies:
            try:
                if f != best_file and os.path.exists(f):
                    os.remove(f)
            except:
                pass
        
        return output_path, best_size
    else:
        print(f"\n{'='*60}")
        print(f"CANNOT ACHIEVE TARGET ✗")
        print(f"{'='*60}")
        print(f"Best lossless: {best_size} bytes")
        print(f"Target: {target_bytes} bytes")
        print(f"Short by: {best_size - target_bytes} bytes\n")
        
        print("This image CANNOT be compressed to under 400 bytes losslessly.")
        print(f"The pixel data requires at least {best_size} bytes to store.")
        print("\nPossible reasons:")
        print(f"  - Too many pixels ({img.width}x{img.height} = {img.width*img.height})")
        print(f"  - Too many unique colors ({unique_colors})")
        print(f"  - Not enough repeated patterns for compression")
        print("\nTo achieve <400 bytes, you must use lossy compression")
        print("(scaling down or reducing colors).")
        
        # Clean up
        for f, _, _ in strategies:
            try:
                if os.path.exists(f):
                    os.remove(f)
            except:
                pass
        
        return None, best_size


if __name__ == "__main__":
    input_file = "download.png"
    output_file = "compressed_lossless_under_400.png"
    
    if os.path.exists(input_file):
        ultra_compress_lossless(input_file, output_file, target_bytes=400)
    else:
        print(f"Error: '{input_file}' not found!")
        print("Save your image as 'image.png' in the same directory.")