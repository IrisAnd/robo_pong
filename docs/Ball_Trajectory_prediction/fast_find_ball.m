function [Centroid , BoundingBox , radius] = fast_find_ball(data , Centroid , box) 

% find the red ball by estimated center mass
% it run faster becase the algorithm search it in small picture
    
    if isempty(Centroid)    % Centroid is empty
        [Centroid , BoundingBox , radius] = find_ball(data); 
        return;
    end
           
    bounds = small_pic(Centroid , box);
    
    if (bounds(2,1) > bounds(2,2))  || (bounds(1,1) > bounds(1,2))  % wrong
        [Centroid , BoundingBox , radius] = find_ball(data); 
        return;
    end
    
    % find in small image
    [temp_pixel , left_box , radius] = find_ball(data(bounds(2,1):bounds(2,2),bounds(1,1):bounds(1,2),:));

    % check if the ball was found
    if isempty(temp_pixel)
        [Centroid , BoundingBox , radius] = find_ball(data); 
    else        
        Centroid = bounds(:,1) + temp_pixel - [1;1];
        BoundingBox = [bounds(:,1) ; 0 ; 0] + left_box;
    end
    
end
    