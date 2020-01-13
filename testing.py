import numpy as np
import matplotlib.pyplot as plt


def main():
    len_y, len_x = 40, 20
    scale = 10

    ground_map = _create_ground_map(scale, len_x, len_y)
    print(ground_map.shape)
    # partial_map = _get_part_of_map(ground_map, scale, len_x, len_y)

    plt.imshow(ground_map) #, extent=[0, len_y, len_x, 0])
    plt.grid()
    plt.show()


def _create_ground_map(scale, len_x, len_y):
    """
    Creates world, numpy array of size scale*(len_x, len_y, 2) defining drivable and non drivable space.
    """
    ground_map = np.zeros((int(scale*len_y), int(scale*len_x)), dtype=int)
    ground_map = _define_drivable_space(ground_map, scale, len_x, len_y) # TODO think
    # TODO possibly other spaces 
    return ground_map

def _define_drivable_space(ground_map, scale, len_x, len_y):
    # TODO implement interactive vizu
    """
    Defines areas of drivable space via interactive vizualisation.
    """
    inds_x = int(len_x * scale)
    inds_y = int(len_y * scale)
    center_x, center_y = inds_x // 2 , inds_y // 2
    ymask, xmask = np.ogrid[0:inds_y, 0:inds_x]

    outter_rad = int(15 * scale)
    inner_rad = int(9 * scale)

    square_mask = (xmask-center_x<outter_rad)&(xmask-center_x>-outter_rad)&(ymask-center_y<outter_rad)&(ymask-center_y>-outter_rad)
    square_mask[center_y-inner_rad+1:center_y+inner_rad,center_x-inner_rad+1:center_x+inner_rad] = False

    circle_mask = (xmask-center_x)**2 + (ymask-center_y)**2 <= outter_rad**2
    inner_circle_mask = (xmask-center_x)**2 + (ymask-center_y)**2 <= inner_rad**2
    circle_mask[inner_circle_mask] = False


    ground_map[square_mask] = 1
    return ground_map


def _get_part_of_map(ground_map, position, scale, orientation, ortho_orientation, distance, width): # TODO finish implementation with angles
    # TODO special cases for orientation = [+-1, 0], [0, +-1]
    len_x_ind, len_y_ind = ground_map.shape
    # rear left and rear right positions
    rl = position + ortho_orientation * width * 0.5
    rr = position - ortho_orientation * width * 0.5
    # front left and front right positions
    fl = position + ortho_orientation * width * 0.5 + orientation * distance
    fr = position - ortho_orientation * width * 0.5 + orientation * distance

    corners = np.array([rl, rr, fl, fr])

    corners_ind = (corners * scale + 0.5).astype(int)

    # # transform corners to indices
    # rl_ind = [int(val * scale + 0.5) for val in rl]
    # rr_ind = [int(val * scale + 0.5) for val in rr]
    # fl_ind = [int(val * scale + 0.5) for val in fl]
    # fr_ind = [int(val * scale + 0.5) for val in fr]

    # # determine subsection of interest of ground map
    # x_min_ind = min(rl_ind[0], rr_ind[0], fl_ind[0], fr_ind[0])
    # x_max_ind = max(rl_ind[0], rr_ind[0], fl_ind[0], fr_ind[0])
    # y_min_ind = min(rl_ind[1], rr_ind[1], fl_ind[1], fr_ind[1])
    # y_max_ind = max(rl_ind[1], rr_ind[1], fl_ind[1], fr_ind[1])
    
    # determine subsection of interest of ground map
    x_min_ind = np.min(corners_ind[:,0])
    x_max_ind = np.max(corners_ind[:,0])
    y_min_ind = np.min(corners_ind[:,1])
    y_max_ind = np.max(corners_ind[:,1])

    if (x_min_ind >= 0) and (x_max_ind <= len_x_ind) and (y_min_ind >= 0) and (y_max_ind <= len_y_ind):
        # if part of map is fully inside ground_map just return part of the map
        coarse_cut_mask = np.ogrid[x_min_ind:x_max_ind, y_min_ind:y_max_ind]
        ground_map_cut = ground_map[tuple(coarse_cut_mask)].copy()

        x_min_ind_cut = x_min_ind
        x_max_ind_cut = x_max_ind
        y_min_ind_cut = y_min_ind
        y_max_ind_cut = y_max_ind

    else:
        # if part of map is partically outside map, pad with BACKGROUND
        ground_map_cut = np.ones((x_max_ind-x_min_ind, y_max_ind-y_min_ind)) * BACKGROUND

        x_min_ind_cut = max(x_min_ind, 0)
        x_max_ind_cut = min(x_max_ind, len_x_ind)
        y_min_ind_cut = max(y_min_ind, 0)
        y_max_ind_cut = min(y_max_ind, len_y_ind)

        # create mask for ground_map
        coarse_cut_mask = np.ogrid[x_min_ind_cut:x_max_ind_cut, y_min_ind_cut:y_max_ind_cut]
        print(coarse_cut_mask[0].shape, coarse_cut_mask[1].shape)
        
        # determine indices to properly shift and cut the ground_map_cut so that shape fits with ground_map[mask]
        zero_shift_x = 0-x_min_ind if x_min_ind < 0 else 0
        zero_shift_y = 0-y_min_ind if y_min_ind < 0 else 0
        len_cut_x = len_x_ind-x_min_ind if x_max_ind > len_x_ind else x_max_ind_cut-x_min_ind
        len_cut_y = len_y_ind-y_min_ind if y_max_ind > len_y_ind else y_max_ind_cut-y_min_ind

        # copy ground_map section to ground_map_cut reagion of interest
        ground_map_cut[zero_shift_x:len_cut_x,zero_shift_y:len_cut_y] = ground_map[tuple(coarse_cut_mask)].copy()

    if True: #orientation in ([1,0], [-1,0], [0,+1], [0,-1]):
        return ground_map_cut # TODO correct ? 
    else:
        corner_xmin = corners[np.argmin(corners[:,0]),:]
        corner_xmax = corners[np.argmin(corners[:,0]),:]
        corner_ymin = corners[np.argmin(corners[:,1]),:]
        corner_ymax = corners[np.argmin(corners[:,1]),:]

        xmask, ymask = np.ogrid[0:ground_map_cut.shape[0], 0:ground_map_cut.shape[0]]

        xmin_ymin_mask = 0.0
        xmax_ymax_cond = 0.0
        xmax_ymin_cond = 0.0
        xmin_ymax_cond = 0.0

        # mask = xmin_ymin_cond or xmax_ymax_cond or xmax_ymin_cond or xmin_ymax_cond


        ground_map_fine_cut = ground_map_cut

        return ground_map_fine_cut







if __name__ == '__main__':
    main()