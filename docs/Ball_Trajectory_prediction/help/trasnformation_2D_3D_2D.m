
% check if the calibration is good

left_pixel = [250 100 ; 550 ,93 ; 170 70]'
right_pixel = [24 100 ; 100 ,93 ; 20 60]'


[left_cord,right_cord] = stereo_triangulation(left_pixel,right_pixel,om,T,...
                                fc_left,cc_left,kc_left,alpha_c_left,...
                                fc_right,cc_right,kc_right,alpha_c_right);
                            

    

 leftpixel=project_points(left_cord,fc_left,cc_left,kc_left,alpha_c_left)
 rightpixel=project_points(right_cord,fc_right,cc_right,kc_right,alpha_c_right)