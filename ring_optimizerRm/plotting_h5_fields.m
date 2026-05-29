clear; clc; close all;
tic

%% Geometric Configuration
thick = [1.6, 4.0, 1.4, 6.7, 30.0, 13.85, 2.2, 10.0, 10.0, 2.2, 13.85, 30.0, 6.7, 1.4, 4.0, 1.6];
names = {'Substrate', 'Coupling Medium', 'Skin', 'Fat', 'Muscle', 'Bone', ...
         'CSF', 'Spinal Cord', 'Spinal Cord', 'CSF', 'Bone', 'Muscle', 'Fat', 'Skin', 'Coupling Medium', 'Substrate'};

%%
h5_files = {'data\e-field (f=1) [1].h5'}; % Adjusted path for current structure

for idx = 1:length(h5_files)
    h5_filename = h5_files{idx};
    if ~exist(h5_filename, 'file')
        fprintf('File not found: %s\n', h5_filename);
        continue;
    end
    fprintf('Processing file %d/%d: %s\n', idx, length(h5_files), h5_filename);

    %% Read mesh and field
    X = h5read(h5_filename, '/Mesh line x');
    Y = h5read(h5_filename, '/Mesh line y');
    Z = h5read(h5_filename, '/Mesh line z');
    E_data = h5read(h5_filename, '/E-Field');
    Ex = complex(E_data.x.re, E_data.x.im);
    Ey = complex(E_data.y.re, E_data.y.im);
    Ez = complex(E_data.z.re, E_data.z.im);

    %% Field
    E_mag = sqrt(abs(Ex).^2 + abs(Ey).^2 + abs(Ez).^2);
    
    % Depth calibration (center the tissue block on 0)
    total_thick = sum(thick);
    z_center_offset = total_thick / 2 - thick(1);
    Z_phys = Z - Z(25) - z_center_offset;

    [X3, Y3, Z3] = meshgrid(X, Y, Z_phys);
    E_mag_perm = permute(E_mag, [2, 1, 3]);

    [~, base_name, ~] = fileparts(h5_filename);
    base_name = sprintf('%d_%s', idx, base_name);

    %% --- Plotting field ---
    fig1 = figure;
    % Slice in the middle of Y (iy=argmin|Y|)
    [~, iy] = min(abs(Y));
    slice(X3, Y3, Z3, E_mag_perm, [], Y(iy), []);
    xlabel('$x$ [mm]','Interpreter','latex'); 
    ylabel('$y$ [mm]','Interpreter','latex'); 
    zlabel('Depth (mm)','Interpreter','latex');
    shading interp; colormap(jet);
    cb = colorbar('northoutside');
    title(cb, '|E| [V/m]', 'FontName', 'Times New Roman', 'FontSize', 10)
    clim([0 100]);
    view([0 0]); % Front view (XZ plane)
    xlim([-28 28]);
    zlim([-total_thick/2 - 5, total_thick/2 + 5]);
    set(gca,'fontname','Times New Roman','fontSize',16)
    set(gcf,'units','centimeters','InnerPosition',[0,0,18,14])

    axis equal
    hold on

    %% --- Tissue Layer Interfaces ---
    current_z = -total_thick / 2;
    % Draw the very first interface
    plot3([-28 28], [Y(iy) Y(iy)], [current_z current_z], 'w-', 'LineWidth', 1);

    for i = 1:length(thick)
        z_end = current_z + thick(i);
        mid_z = (current_z + z_end) / 2;
        
        % Draw interface lines
        plot3([-28 28], [Y(iy) Y(iy)], [z_end z_end], 'w-', 'LineWidth', 1);
        
        % Add text
        if strcmp(names{i}, 'CSF')
            plot3([-28 28], [Y(iy) Y(iy)], [current_z current_z], 'r-', 'LineWidth', 1.5);
            plot3([-28 28], [Y(iy) Y(iy)], [z_end z_end], 'r-', 'LineWidth', 1.5);
            text(30, Y(iy), mid_z, names{i}, 'Color', 'r', 'FontSize', 8, 'FontWeight', 'bold');
        else
            text(30, Y(iy), mid_z, names{i}, 'Color', 'k', 'FontSize', 8);
        end
        
        current_z = z_end;
    end
end
toc