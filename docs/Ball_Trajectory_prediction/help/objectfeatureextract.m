 
%Step 1: Read Image

mobj =mmreader('video1.avi');
currentframe = read(mobj,1);
%imshow(currentframe);
numItr  = mobj.NumberOfFrames;
fpss = mobj.FrameRate;
vid1 = read(mobj);

% Create a MATLAB movie struct from the video frames.
       for k = 1 : numItr
          mov(k).cdata = vid1(:,:,:,k);
            mov(k).colormap = [];
           imshow(mov(k).cdata);
           imagename=strcat(int2str(k), '.jpg');
           imwrite(mov(k).cdata, strcat('frame',imagename));
             %extractComponents(mov(k).cdata);
       end
 
       % Create a figure
       hf = figure; 
       
        % Resize figure based on the video's width and height
      set(hf, 'position', [350 350 mobj.Width mobj.Height])
 
       % Playback movie once at the video's frame rate
       movie(hf, mov, 1, mobj.FrameRate);

 %%          
  
centroid=zeros(numItr,8);      
i=1;
while i<=numItr
   
    prevframe = currentframe;
    currentframe = read(mobj,i);
   imshow(currentframe);
    J = imabsdiff(currentframe,prevframe);
    imshow(J);
    
    
      I = im2single(rgb2gray(J));
    
    %I = propsSynthesizeImage;
    %imshow(I)
    [level EM] = graythresh(J);
  
    BW = im2bw(J,level);
  imshow(BW);

% [D,L] = bwdist(BW,'euclidean');

   
   bc = imclose(BW,strel('disk',5));
   
F = medfilt2(bc);
   
  [L2, NUM] = bwlabel(F,4);
 
  cardata = regionprops(L2,BW,{'Centroid','BoundingBox','ConvexHull','Area'});

  
  
conHull =cat(1,cardata.ConvexHull);
%contour(conHull);

x=[cardata.Centroid];
centroid(i,1:length(x)) = [cardata.Centroid];
%disp(centroid);
bbox = [cardata.BoundingBox]; 

area = [cardata.Area];
axis on
hold on
% Plot Bounding Box
for n=1:size(cardata,1)
    rectangle('Position',cardata(n).BoundingBox,'EdgeColor','g','LineWidth',2)
end
hold off
%pause (1)

%%plot centroid
hold on 
numObj = numel(cardata);
for k = 1 : numObj
 plot(cardata(k).Centroid(1), cardata(k).Centroid(2), 'r*');
 [D, L] = bwdist(BW,'euclidean');
subplot(2, 1, 1)
plot((1:500), cardata(k).Centroid(1)), ylabel('x');
subplot(2, 1, 2)
plot((1:500), cardata(k).Centroid(2)), ylabel('y');
xlabel('time (cardata)') 

end
hold off
%hold on
%numObj = numel(cardata);
%for k = 1 : numObj
    %
   % plot(cardata(k).Centroid(1), cardata(k).Centroid(2), 'r*');
  
%end
%hold off
  
i=i+1;   
end


% h = figure;
 %   F = getframe(h);
  %  [M,map] = frame2im(F);
    


   
%I = imread('frame2.jpg');
  %Ii = rgb2gray(I);
  %imshow(I);
  % image = step(hidtc,Ii);
 
