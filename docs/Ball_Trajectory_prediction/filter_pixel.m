function fix_pixel = filter_pixel(pixel)

% delete pixels out of picture

for i = 1:length(pixel)
    if pixel(1,i) < 0 || pixel(1,i) > 640 || pixel(2,i) < 0 || pixel(2,i) > 480
       break;
    end
end
fix_pixel=pixel(:,1:i-1);
end