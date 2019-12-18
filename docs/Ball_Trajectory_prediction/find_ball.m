function [Center , Bounding , radius] = find_ball(data) 
    
    % Algorithm from mathworks by A. Bhargav Anand

    % Now to track red objects in real time
    % we have to subtract the red component 
    % from the grayscale image to extract the red components in the image.
    diff_im = imsubtract(data(:,:,1), rgb2gray(data));
    %Use a median filter to filter out noise
    diff_im = medfilt2(diff_im, [3 3]);
    % Convert the resulting grayscale image into a binary image.
    diff_im = im2bw(diff_im,0.18);
    
    % Remove all those pixels less than 300px
    diff_im = bwareaopen(diff_im,300);
    
    % Label all the connected components in the image.
    diff_im = logical(bwlabel(diff_im, 8));
    
    % Here we do the image blob analysis.
    % We get a set of properties for each labeled region.
    stats = regionprops(diff_im, 'BoundingBox', 'Centroid','Area');   %   
    
    if isempty(stats)
        Center = [];
        Bounding = [];
        radius = [];
        return;
    end
    
    Center = stats(1).Centroid';
    Bounding = stats(1).BoundingBox';
    radius = sqrt(stats(1).Area/pi);
    
end