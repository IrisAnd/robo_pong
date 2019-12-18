
close all


% load images
LEFT_PICTURES_ARR=[];
RIGHT_PICTURES_ARR=[];

for i=1:80
   a=num2str(i);
   b=strcat('jpg\left',a,'.jpg');
   LEFT_PICTURES_ARR{i}=imread(b); 
   
   b=strcat('jpg\right',a,'.jpg');
   RIGHT_PICTURES_ARR{i}=imread(b); 
   
end
%%

load Calib_Results.mat

% show pictures in slow motion
fig=figure(1);
subplot(2, 2, [1,3]);

len1=length(LEFT_PICTURES_ARR); % number of pictures
h1=imshow(LEFT_PICTURES_ARR{1});
line1=line(4*rand(1,100),4*rand(1,100));
line2=line(4*rand(1,100),4*rand(1,100));
rect1=rectangle('Position',[1 2 3 4],'EdgeColor','r','LineWidth',2);
rect2=rectangle('Position',[1 2 3 4],'EdgeColor','r','LineWidth',2);

line7=line(4*rand(1,100),4*rand(1,100));
line8=line(4*rand(1,100),4*rand(1,100));

subplot(2, 2, 2);
line3=line(4*rand(1,100),4*rand(1,100),4*rand(1,100));
line4=line(4*rand(1,100),4*rand(1,100),4*rand(1,100));
line(0,0,0,'Color', [0 1 0],'Marker' ,'+','LineWidth',20);
axis([-2000 2000 0 6000 -1000 2000]);
grid on

subplot(2, 2, 4);
line(0,0,0,'Color', [0 1 0],'Marker' ,'+','LineWidth',20);
line5=line(4*rand(1,100),4*rand(1,100),4*rand(1,100));
axis([-2000 2000 0 6000 -1000 2000]);
grid on
subplot(2, 2, [1,3]);

tic;
m=6; % number of past points
time=toc;
t=linspace(time-0.04*m,time,m);

left_last_pixels=[];
right_last_pixels=[];

box=70;
left_pixel=[];
right_pixel=[];


arr_pixels_x=0;
arr_pixels_y=0;
arr_pixels_z=0;
i=0;
flag=1;

% pause();
% writerObj = VideoWriter('project8.avi');
% writerObj.FrameRate = 20;
% open(writerObj);

while(1)
    
    pause(0.05);
    if i==len1
        arr_pixels_x=0;
        arr_pixels_y=0;
        arr_pixels_z=0;
        flag=1;
    end
    
%     frame = getframe(fig);
%     writeVideo(writerObj,frame);

    
    i=mod(i,len1) + 1;   % i=i+1;
    left_pic=LEFT_PICTURES_ARR{i};
    right_pic=RIGHT_PICTURES_ARR{i};
    
    % find the red ball
    [left_pixel  ,  left_box , radius] = fast_find_ball(left_pic  , left_pixel  , box);     
    [right_pixel , right_box] = fast_find_ball(right_pic , right_pixel , box);
    
    set(h1,'cdata',left_pic);
    
    % if the ball wasn't found at least in one pic
    if isempty(left_pixel) || isempty(right_pixel) 
        left_last_pixels=[]; 
        right_last_pixels=[];
        flag=1;
        continue;
    end
    
    % this picture has the ball and picture before does not have the ball
    % this like the first time
    if flag
        left_last_pixels=[];
        right_last_pixels=[];
        for j=1:m
            left_last_pixels  = [left_last_pixels , left_pixel];
            right_last_pixels = [right_last_pixels , right_pixel];
        end
        time=toc;
        t=linspace(time-1*m,time,m);
        flag=0; 
    end
    
    % create 1*m vector for time and motion
    left_last_pixels  = [left_last_pixels(:,2:m) , left_pixel];
    right_last_pixels = [right_last_pixels(:,2:m) , right_pixel];
    t=[t(2:m),toc];
     
    
    set(line1,'xdata',left_last_pixels(1,:),'ydata',left_last_pixels(2,:) ,...
                'LineStyle' ,'-' ,'Marker' ,'+','Color', [0 0 1]);  
    
%     set(rect1,'Position',left_box,'EdgeColor','r','LineWidth',2);

    c = -1*radius: radius/20 : 1*radius;
    r = sqrt(radius^2-c.^2);
    set(line7,'xdata',left_pixel(1) + c,'ydata',left_pixel(2) + r ,...
                'LineStyle' ,'-' ,'Marker' ,'.','Color', [0 1 0]);
    set(line8,'xdata',left_pixel(1) + c,'ydata',left_pixel(2) - r ,...
        'LineStyle' ,'-' ,'Marker' ,'+','Color', [0 1 0]);
    

    % find the ball cordinate
    [left_cord,right_cord] = stereo_triangulation(left_last_pixels,right_last_pixels,om,T,...
                                fc_left ,cc_left ,kc_left ,alpha_c_left,...
                                fc_right,cc_right,kc_right,alpha_c_right);
                            
    set(line3,'xdata',left_cord(1,:),'ydata',left_cord(3,:) ,...
                'zdata',-left_cord(2,:),'LineStyle' ,'-' ,'Marker' ,'+','Color', [0 0 1]);
   
    % estimate the tracking
    
    left_vector  = estimate_vector2(left_cord,t,70);
    right_vector = estimate_vector2(right_cord,t,10);
    
    set(line4,'xdata',left_vector(1,:),'ydata',left_vector(3,:) ,...
                'zdata',-left_vector(2,:),'LineStyle','-','Marker' ,'+','Color', [1 0 1]);
    
    
    arr_pixels_x(i)=left_cord(1,m);
    arr_pixels_y(i)=left_cord(3,m);
    arr_pixels_z(i)=left_cord(2,m);
    
    start_sh = (i-50)*((i-50)>0)+1;
    set(line5,'xdata',arr_pixels_x(start_sh:i),'ydata',arr_pixels_y(start_sh:i) ,...
            'zdata',-arr_pixels_z(start_sh:i),'LineStyle' ,'-' ,'Marker' ,'.'...
            ,'LineWidth',5,'Color', [1 0 0]);
    
    
    % convert to pixel in one camera
    
    new_left_pixels  = project_points(left_vector,fc_left,cc_left,kc_left,alpha_c_left);
    new_right_pixels = project_points(right_vector,fc_right,cc_right,kc_right,alpha_c_right); 
    
    % delete pixel out of picture
    
    fix_left_pixels = filter_pixel(new_left_pixels);
    
    fix_right_pixels = filter_pixel(new_right_pixels);
    
    if isempty(fix_left_pixels) || isempty(fix_right_pixels)  % no future
        left_pixel=[];    % for the next picture
        right_pixel=[];    % for the next picture
        continue;
    end
    
    % the new pixel that estimated
    len_left = length(fix_left_pixels(1,:));
    len_right = length(fix_right_pixels(1,:));
    num_pixel=5;
    left_pixel  = fix_left_pixels(:,num_pixel*(num_pixel<len_left) + 1);
    right_pixel = fix_right_pixels(:,num_pixel*(num_pixel<len_right) + 1);
    
    temp_box = small_pic(left_pixel , box);
    
    left_box_future = [temp_box(:,1) ; temp_box(:,2) - temp_box(:,1)];
       
    % plot the tracking on the picture
 
    set(line2,'xdata',fix_left_pixels(1,:),'ydata',fix_left_pixels(2,:) ,...
                'LineStyle' ,'-' ,'Marker' ,'+','Color', [1 0 1]);          
              
    set(rect2,'Position',left_box_future,'EdgeColor',[0 1 1],'LineWidth',2);
    
end
close(writerObj);

i/toc