clear; clc; close all;
tic

%%
h5_files = {'campi_wo\e-field (f=1.25) [1].h5'};

for idx = 1:length(h5_files)
    h5_filename = h5_files{idx};
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
    E_mag = sqrt(real(Ex).^2 + real(Ey).^2 + real(Ez).^2);
    E_mag_perm = permute(E_mag, [2, 1, 3]);
    [X3, Y3, Z3] = meshgrid(X, Y, Z);

    [~, base_name, ~] = fileparts(h5_filename);
    base_name = sprintf('%d_%s', idx, base_name);

    %% --- Plotting field ---
    fig1 = figure;
    slice(X3, Y3, Z3, E_mag_perm, -15, -65, 20);
    xlabel('$x$ [mm]','Interpreter','latex'); 
    ylabel('$y$ [mm]','Interpreter','latex'); 
    zlabel('$z$ [mm]','Interpreter','latex');
    shading interp; colormap(jet);
    cb = colorbar('northoutside');
    title(cb, '|E| [V/m]', 'FontName', 'Times New Roman', 'FontSize', 10)
    clim([0 100]);
    % view([0 1 0]);
    xlim([-100 100]); ylim([-100 100]); zlim([-100 100]);
    set(gca,'fontname','Times New Roman','fontSize',16)
    set(gcf,'units','centimeters','InnerPosition',[0,0,11,11])

    axis equal
    xticks([-50 0 50])
    yticks([-50 0 50])
    zticks([-50 0 50])
    hold on

end