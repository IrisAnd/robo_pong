
close all


% load images
LEFT_PICTURES_ARR=[];
RIGHT_PICTURES_ARR_TEMP=[];

for i=1:80
   a=num2str(i);
   b=strcat('/home/airish/Schreibtisch/NTU/Robotics/Resources/Ball_Trajectory_prediction/example/jpg/left',a,'.jpg');
   LEFT_PICTURES_ARR{i}=imread(b); 
   
   b=strcat('/home/airish/Schreibtisch/NTU/Robotics/Resources/Ball_Trajectory_prediction/example/jpg/right',a,'.jpg');
   RIGHT_PICTURES_ARR_TEMP{i}=imread(b); 
   
end
%%
load data.mat
% show pictures in slow motion
fig=figure(1);
subplot(2, 2, [1 ,3]);

len1=length(LEFT_PICTURES_ARR); % number of pictures
h=imshow(LEFT_PICTURES_ARR{1});
line1=line(4*rand(1,100),4*rand(1,100));
line2=line(4*rand(1,100),4*rand(1,100));
rect1=rectangle('Position',[1 2 3 4],'EdgeColor','r','LineWidth',2);
rect2=rectangle('Position',[1 2 3 4],'EdgeColor','r','LineWidth',2);


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


arr_pixels_x=0;
arr_pixels_y=0;
arr_pixels_z=0;
i=0;

% writerObj = VideoWriter('project.avi');
% writerObj.FrameRate = 20;
% open(writerObj);

while (1)
   %%
   pause(0.05);         % slow motion
   if i==len1
        arr_pixels_x=0;
        arr_pixels_y=0;
        arr_pixels_z=0;
   end
   i=mod(i,len1) + 1;   % i=i+1;
%    frame = getframe;
%    writeVideo(writerObj,frame);   
   set(h,'cdata',LEFT_PICTURES_ARR{i});
    
   past_pixels    =   LEFT_PIXELS_PAST_ARR{i};
   future_pixels  =   LEFT_PIXELS_FUTURE_ARR{i};
   
   past_vector = LEFT_CORD_PAST_VECTOR{i};
   future_vector = LEFT_CORD_FUTURE_VECTOR{i};
   
    
   if ~isempty(past_pixels)
       
       len_past     = length(past_pixels(1,:));
       
       set(line1,'xdata',past_pixels(1,:),'ydata',past_pixels(2,:) ,...
                'LineStyle' ,'-' ,'Marker' ,'+','Color', [0 0 1]);
            
       set(rect1,'Position',LEFT_BOX_PAST_ARR{i},'EdgeColor','r','LineWidth',2);
       
       set(line3,'xdata',past_vector(1,:),'ydata',past_vector(3,:) ,...
                'zdata',-past_vector(2,:),'LineStyle' ,'-' ,'Marker' ,'+','Color', [0 0 1]);
       
       % plot 3D cordinate
       
       arr_pixels_x(i)=past_vector(1,len_past);
       arr_pixels_y(i)=past_vector(3,len_past);
       arr_pixels_z(i)=past_vector(2,len_past);
       
       start_sh = (i-50)*((i-50)>0)+1;
       set(line5,'xdata',arr_pixels_x(start_sh:i),'ydata',arr_pixels_y(start_sh:i) ,...
                'zdata',-arr_pixels_z(start_sh:i),'LineStyle' ,'-' ,'Marker' ,'.'...
                ,'LineWidth',5,'Color', [1 0 0]);
   else
       continue;    % no past
   end
   
   if ~isempty(future_pixels) 
       
       len_future   = length(future_pixels(1,:));
          
       set(line2,'xdata',future_pixels(1,:),'ydata',future_pixels(2,:) ,...
                'LineStyle' ,'-' ,'Marker' ,'+','Color', [1 0 1]); 

       set(rect2,'Position',LEFT_BOX_FUTURE_ARR{i},'EdgeColor',[0 1 1],...
                    'LineWidth',2); 
                
      
       set(line4,'xdata',future_vector(1,:),'ydata',future_vector(3,:) ,...
                'zdata',-future_vector(2,:),'LineStyle','-','Marker' ,'+','Color', [1 0 1]);
   end
   

   
end

% close(writerObj);