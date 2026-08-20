import math, sprites

FILEGUIDE = '''This file is used to scale the sprites in sprites.py to different sizes.'''

# Memoization cache for intermediate grids
_intermediate_cache = {}

def scale_sprite(sprite, old_size, new_size):
    lcm = math.lcm(old_size, new_size)
    scale_up = lcm // old_size
    scale_down = lcm // new_size
    
    # Create cache key - use id() for faster hashing on large sprites
    sprite_id = id(sprite)
    inter_cache_key = (sprite_id, old_size, lcm)
    
    # Check if intermediate grid already computed
    if inter_cache_key in _intermediate_cache:
        inter_grid = _intermediate_cache[inter_cache_key]
    else:
        # Scale up: duplicate each pixel horizontally, then duplicate rows vertically
        # Result: lcm × lcm grid
        inter_grid = []
        for row in sprite:
            # Duplicate each pixel horizontally
            scaled_row = []
            for pixel in row:
                scaled_row.extend([pixel] * scale_up)
            # Duplicate the row vertically
            for _ in range(scale_up):
                inter_grid.append(scaled_row[:])
        # Cache the intermediate grid
        _intermediate_cache[inter_cache_key] = inter_grid
    
    # Scale down: average blocks of scale_down × scale_down
    new_grid = []
    for i in range(0, len(inter_grid), scale_down):
        chunk_rows = inter_grid[i:i+scale_down]
        new_row = []
        
        for j in range(0, len(chunk_rows[0]), scale_down):
            vr = []
            vg = []
            vb = []
            trans = 0
            
            # Average the block
            for row in chunk_rows:
                for pixel in row[j:j+scale_down]:
                    if pixel == -1:
                        trans += 1
                    else:
                        vr.append(pixel[0])
                        vg.append(pixel[1])
                        vb.append(pixel[2])
            
            # Determine output pixel
            if trans > (scale_down ** 2) * 0.8:
                new_row.append(bytearray([0, 0, 0, 1]))
            else:
                if vr:
                    new_row.append(bytearray([sum(vr) // len(vr), sum(vg) // len(vg), sum(vb) // len(vb), 0]))
                else:
                    new_row.append(bytearray([0, 0, 0, 1]))
        
        new_grid.append(new_row)
    
    return new_grid

if __name__ == "__main__":
    with open("scaled_sprites.txt", "wb") as file:
        print("File opened\nScaling sprites...")
        for sprite in sprites.SPRITES:
            for size in range(1, 33):
                if sprite != "motel_sprite" and sprite != "car_left" and sprite != "car_right":
                    result = scale_sprite(sprites.SPRITES[sprite], 16, size)
                    b = bytearray()
                    for row in result:
                        for pixel in row:
                            b += pixel
                    file.write(b)
                    print(f"Scaled {sprite} to size {size}")
                elif sprite == "motel_sprite":
                    chunks = [sprites.SPRITES[sprite][i:i+16] for i in range(0, len(sprites.SPRITES[sprite]), 16)]
                    b = bytearray()
                    for chunk in chunks:
                        new_chunk = [[] for _ in range(size)]  # Should be size, not len(chunk)
                        for i in range(len(chunk[0])//16):
                            new_block = []
                            for row in chunk:
                                new_block.append(row[i*16:(i+1)*16])
                            result = scale_sprite(new_block, 16, size)
                            for row_idx, row in enumerate(result):
                                new_chunk[row_idx].extend(row)
                        for row in new_chunk:
                            for pixel in row:
                                b += pixel
                    file.write(b)
                    print(f"Scaled {sprite} to size {size}")