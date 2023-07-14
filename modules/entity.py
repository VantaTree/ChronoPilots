import pygame
from .config import *
from .engine import *
from .objects import objects_hitboxes

def do_collision(entity, axis, master, obj_rects=None):

    px = int(entity.hitbox.centerx / TILESIZE)
    py = int(entity.hitbox.centery / TILESIZE)

    for y in range(py-1, py+2):
        for x in range(px-1, px+2):

            if x < 0 or y < 0: continue

            cell = get_xy(master.level.collision, x, y)
            if cell is None or cell <= 0: continue

            rect = pygame.Rect(x*TILESIZE, y*TILESIZE, TILESIZE, TILESIZE)
            if not entity.hitbox.colliderect(rect): continue

            apply_collision(master, entity, axis, rect, cell)

    if axis != 2:
        for rect in obj_rects:
            if not entity.hitbox.colliderect(rect): continue
            apply_collision(master, entity, axis, rect)


def apply_collision(master, entity, axis, rect, cell=1):

    if axis == 0: # x-axis

                if cell in (1, 2):

                    if entity.velocity.x > 0:
                        entity.hitbox.right = rect.left
                    if entity.velocity.x < 0:
                        entity.hitbox.left = rect.right

    elif axis == 1: # y-axis

        if cell in (1, 2):
            if entity.velocity.y < 0:
                entity.hitbox.top = rect.bottom
            if entity.velocity.y > 0:
                entity.hitbox.bottom = rect.top

    elif axis == 2: # slants
            
        if   cell == 4: # ◢
            gapy = rect.bottom - entity.hitbox.bottom
            gapx = entity.hitbox.right - rect.left
            if gapx < gapy: return
            prev_pos = entity.hitbox.right - entity.velocity.x, entity.hitbox.bottom - entity.velocity.y
            entity.hitbox.bottomright = prev_pos
            if entity.velocity.x > 0 and entity.velocity.y > 0:
            # if entity.velocity.x and entity.velocity.y:
                entity.velocity.update()
            elif entity.velocity.x > 0:
                entity.velocity.y = 0
                new_vel = entity.velocity.rotate(-45)
                entity.hitbox.move_ip(new_vel)
            elif entity.velocity.y > 0:
                entity.velocity.x = 0
                new_vel = entity.velocity.rotate(45)
                entity.hitbox.move_ip(new_vel)
        elif cell == 5: # ◣
            gapy = rect.bottom - entity.hitbox.bottom
            gapx = rect.right - entity.hitbox.left
            if gapx < gapy: return
            prev_pos = entity.hitbox.right - entity.velocity.x, entity.hitbox.bottom - entity.velocity.y
            entity.hitbox.bottomright = prev_pos
            if entity.velocity.x < 0 and entity.velocity.y > 0:
            # if entity.velocity.x and entity.velocity.y:
                entity.velocity.update()
            elif entity.velocity.x < 0:
                entity.velocity.y = 0
                new_vel = entity.velocity.rotate(45)
                entity.hitbox.move_ip(new_vel)
            elif entity.velocity.y > 0:
                entity.velocity.x = 0
                new_vel = entity.velocity.rotate(-45)
                entity.hitbox.move_ip(new_vel)
        elif cell == 6: # ◤
            gapy = entity.hitbox.top - rect.top
            gapx = rect.right - entity.hitbox.left
            if gapx < gapy: return
            prev_pos = entity.hitbox.x - entity.velocity.x, entity.hitbox.y - entity.velocity.y
            entity.hitbox.topleft = prev_pos
            if entity.velocity.x < 0 and entity.velocity.y < 0:
            # if entity.velocity.x and entity.velocity.y:
                entity.velocity.update()
            elif entity.velocity.x < 0:
                entity.velocity.y = 0
                new_vel = entity.velocity.rotate(-45)
                entity.hitbox.move_ip(new_vel)
            elif entity.velocity.y < 0:
                entity.velocity.x = 0
                new_vel = entity.velocity.rotate(45)
                entity.hitbox.move_ip(new_vel)
        elif cell == 7: # ◥
            gapy = entity.hitbox.top - rect.top
            gapx = entity.hitbox.right - rect.left
            if gapx < gapy: return
            prev_pos = entity.hitbox.right - entity.velocity.x, entity.hitbox.y - entity.velocity.y
            entity.hitbox.topright = prev_pos
            if entity.velocity.x > 0 and entity.velocity.y < 0:
            # if entity.velocity.x and entity.velocity.y:
                entity.velocity.update()
            elif entity.velocity.x > 0:
                entity.velocity.y = 0
                new_vel = entity.velocity.rotate(45)
                entity.hitbox.move_ip(new_vel)
            elif entity.velocity.y < 0:
                entity.velocity.x = 0
                new_vel = entity.velocity.rotate(-45)
                entity.hitbox.move_ip(new_vel)

                        
def get_xy(grid, x, y):

    if x < 0 or y < 0: return
    try:
        return grid[y][x]
    except IndexError: return

def get_obj_rects(entity, master):

    obj_rects = []
    px1 = int(entity.rect.left//CHUNK)
    px2 = px1 + entity.rect.width//CHUNK +1
    py1 = int(entity.hitbox.top//CHUNK)
    py2 = py1 + entity.rect.height//CHUNK +1

    for y in range(py1-1, py2+1):
        for x in range(px1, px2+1):
            obj_list = master.level.object_chunk.get((x, y))
            if obj_list is None: continue
            for obj in obj_list:
                id = master.level.data.tiledgidmap[obj.gid] - master.level.object_firstgid +1
                try:
                    a, b, w, h = objects_hitboxes[id]
                except TypeError: continue
                rect = pygame.FRect(a, b, w, h)
                rect.centerx += obj.x+((obj.width-w)/2)
                rect.bottom += obj.y+obj.height-h
                obj_rects.append(rect)
    obj_rects.extend(master.level.object_hitboxes)

    return obj_rects