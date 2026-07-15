function [f_GHz,epsr,sigm] = Keyisight_data_reading(name,n,num_samp,eps0,mod)
%
epsr = zeros(n,num_samp); %number of measures on validation
sigm = epsr;
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% mod == 0 : single acquisition
% mod != 0 : multiple acqusitions
if mod == 0
   num = n;
   fileID = fopen(string(name) + num2str(num) + ".prn", 'r');
   reader = textscan(fileID, '%f32 %f32 %f32', 201, 'HeaderLines', 1);
   epsr = reader{2}';
   eps2 = reader{3};
   fclose(fileID);
   f_GHz = reader{1}/1e9;
   sigm = eps2 * 2 * pi .* f_GHz * 1e9 * eps0;
   f_GHz = f_GHz';
else
    for num = 1:n
        fileID = fopen(string(name) + num2str(num) + ".prn", 'r');
        reader = textscan(fileID, '%f32 %f32 %f32', 201, 'HeaderLines', 1);
        epsr(num, :) = reader{2}';
        eps2 = reader{3};
        fclose(fileID);
        f_GHz = reader{1}/1e9;
        sigm(num, :) = eps2 * 2 * pi .* f_GHz * 1e9 * eps0;
        f_GHz = f_GHz';
    end
end
clear reader eps2