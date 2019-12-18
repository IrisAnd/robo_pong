%profile on
objectfeatureextract;
a=centroid(:,1);
b=centroid(:,2);
dist=mani_dist(a,b);
dist=[dist;0];
vel=mani_vel(dist);
%ac=mani_acc(vel);
%frames=[1:120]';



hbfr = video.MultimediaFileReader('Filename','video5.avi');
%hVidReader = video.MultimediaFileReader(filename, 'ImageColorSpace', 'RGB',...
 %                             'VideoOutputDataType', 'single');
 
 


 hcr = video.ChromaResampler(...
  'Resampling', '4:2:0 (MPEG1) to 4:4:4', ...
  'InterpolationFilter', 'Pixel replication');

hcsc1 = video.ColorSpaceConverter('Conversion', 'YCbCr to RGB');
hcsc2 = video.ColorSpaceConverter('Conversion', 'RGB to intensity');

hidtc = video.ImageDataTypeConverter('OutputDataType', 'single');

hof = video.OpticalFlow( ...
    'Method', 'Horn-Schunck',...
    'ReferenceFrameSource', 'Property',...
    'OutputValue', 'Horizontal and vertical components in complex form', ...
    'ReferenceFrameDelay', 3);


hMean1 = video.Mean;
hMean2 = video.Mean('RunningMean', true);

hMedianFilt = video.MedianFilter2D;
hclose = video.MorphologicalClose('Neighborhood', strel('line',5,45));

hblob = video.BlobAnalysis( ...
                    'CentroidOutputPort', false, 'AreaOutputPort', true, ...
    'BoundingBoxOutputPort', true, 'ExtentOutputPort', true, ...
    'OutputDataType', 'double', ...
    'ExcludeBorderBlobs',true,...
                'MaximumCount', 80);


herode = video.MorphologicalErode('Neighborhood', strel('square',2));

hshapeins1 = video.ShapeInserter('BorderColor', 'Custom', ...
                                  'CustomBorderColor', [0 1 0]);
hshapeins2 = video.ShapeInserter( 'Shape','Lines', ...
                                   'BorderColor', 'Custom', ...
                                   'CustomBorderColor', [255 255 0]);
                               
 htextins = video.TextInserter('Text', '%4d', 'Location',  [1 1], ...
                               'Color', [1 1 1], 'FontSize', 12);

hVideo1 = video.VideoPlayer('WindowCaption', 'Original Video');
hVideo1.WindowPosition(1) = round(0.4*hVideo1.WindowPosition(1)) ;
hVideo1.WindowPosition(2) = round(1.5*(hVideo1.WindowPosition(2))) ;
hVideo1.WindowPosition([4 3]) = [200 200];

hVideo2 = video.VideoPlayer('WindowCaption', 'Motion Vector');
hVideo2.WindowPosition(1) = hVideo1.WindowPosition(1) + 350;
hVideo2.WindowPosition(2) =round(1.5* hVideo2.WindowPosition(2));
hVideo2.WindowPosition([4 3]) = [200 200];

hVideo3 = video.VideoPlayer('WindowCaption', 'Thresholded Video');
hVideo3.WindowPosition(1) = hVideo2.WindowPosition(1) + 350;
hVideo3.WindowPosition(2) = round(1.5*(hVideo3.WindowPosition(2))) ;
hVideo3.WindowPosition([4 3]) = [200 200];

hVideo4 = video.VideoPlayer('WindowCaption', 'Results');
hVideo4.WindowPosition(1) = hVideo1.WindowPosition(1);
hVideo4.WindowPosition(2) = round(1.5*(hVideo4.WindowPosition(2))) ;
hVideo4.WindowPosition([4 3]) = [200 200];





%sz = get(0,'ScreenSize');
%pos = [20 sz(4)-300 200 200];
%hVideo1 = video.VideoPlayer('WindowCaption','Original Video','WindowPosition',pos);
%pos(1) = pos(1)+220; % move the next viewer to the right
%hVideo2 = video.VideoPlayer('WindowCaption','Motion Vector','WindowPosition',pos);
%pos(1) = pos(1)+220;
%hVideo3 = video.VideoPlayer('WindowCaption','Thresholded Video','WindowPosition',pos);
%pos(1) = pos(1)+220;
%hVideo4 = video.VideoPlayer('WindowCaption','Results','WindowPosition',pos);

% Initialize variables used in plotting motion vectors.

MotionVecGain = 20;
startline_row =  200;
lastline_row = 60;
borderOffset   = 5;
decimFactorRow = 5;
decimFactorCol = 5;
firstTime = true;
while ~isDone(hbfr)
   % [y, cb, cr] = step(hbfr);      % Read input video frame
  %[cb, cr] = step(hcr, cb, cr);
   % imrgb = step(hcsc1, cat(3,y,cb,cr)); % Convert image from YCbCr to RGB
   imrgb = step(hbfr); 
   image = step(hidtc, imrgb);          % Convert image to single
    I = step(hcsc2, image);        % Convert color image to intensity
    of = step(hof, I);             % Estimate optical flow
    
    VSQ = step(hof,I);
    % Thresholding and Region Filtering.
    y1 = of .* conj(of);
    % Compute the velocity threshold from the matrix of complex velocities.
    vel_th = 0.5 * step(hMean2, step(hMean1, y1));
    
  
    % Threshold the image and then filter it to remove fine speckle noise.
    filteredout = step(hMedianFilt, y1 >= vel_th);

    % Perform erosion operation to thin-out the parts of the road followed
    % by the closing operation to remove gaps in the blobs.
    th_image = step(hclose, step(herode, filteredout));

    % Regional Filtering.

    % Estimate the area and bounding box of the blobs in the thresholded
    % image.
    
    [area, bbox, extent] = step(hblob, th_image);
    
   
    
      
    % Select those boxes which are in our ROI.
    Idx = bbox(1,:) > startline_row;
   
    isCar = extent > 0.4;
    numCars = sum(isCar);   % Number of cars
    bbox(:,~isCar) = int32(-1);   
    
       
    %[Count]= step(hblob,th_image);
    
    
    
    % Draw bounding rectangles around the tracked cars.
    y2 = step(hshapeins1, image, bbox);

    % Display the number of cars tracked and a white line showing ROI.
    y2(22:23,:,:) = 1;             % The white line.
    y2(1:15,1:30,:) = 0;           % Background for displaying count
    image_out = step(htextins, y2,int32(numCars));

    % Generate the coordinate points for plotting motion vectors.
    if firstTime
      [R C] = size(of);            % Height and width in pixels
      RV = borderOffset:decimFactorRow:(R-borderOffset);
      CV = borderOffset:decimFactorCol:(C-borderOffset);
      [Y X] = meshgrid(CV,RV);
      firstTime = false;
    end

    % Calculate and draw the motion vectors.
    tmp = of(RV,CV) .* MotionVecGain;
    lines = [X(:)';Y(:)';X(:)' + imag(tmp(:))';Y(:)' + real(tmp(:))'];
    mv_video = step(hshapeins2, image, lines);

    
    
   % Real_part = real(of(:));
  % Imag_part = imag(of(:));
    
   % step(hVideo1, image);          % Display Original Video
    step(hVideo2, mv_video);       % Display video with motion vectors
   % step(hVideo3, th_image);       % Display Thresholded Video
    step(hVideo4, image_out);      % Display video with bounding 
    
end

close(hVideo1)
close(hVideo2)
close(hVideo3)
close(hbfr)
%RR=Real_part(1000:end);
%RI=Imag_part(1000:end);
%d1=mani_dist(RR,RI);
figure,plot(vel);title('Velocity');
