close all
clear
clc
%% VALIDATION 
% Peyman model for saline solution (reference)
f = 300e6:1e6:14e9; %frequency range
T = input('Temperature: '); % °C
M = 0.1; %Molarity of saline solution mol/l
%
eps0 = 8.8542e-12;
compPerm = NaCl_0to1M_5to35C(f, T, M);
% 
%%  Data reading from .prn file (works as a .txt)
num_samp = 201; %number of samples
n = 2;
%
name_VAL = 'VAL_';
%name_FCSF = input('FCSF name:');
name_NJ = 'NJ_'; %Neck juice
%
[f_GHz,epsr,sigm] = Keyisight_data_reading(name_VAL,n,num_samp,eps0,1);
%
mean_ep_r = mean(epsr);
f_bar_ind = [26;55;85;114;143;172];
max_err_ep_r = max(epsr) - mean_ep_r;
min_err_ep_r = mean_ep_r - min(epsr);
%
mean_sigma = mean(sigm);
max_err_sigma = max(sigm) - mean_sigma;
min_err_sigma = mean_sigma - min(sigm);
%
figure
subplot(1,2,1)
plot(f/1e9,real(compPerm),':g','LineWidth',2);
hold on
plot(f_GHz,mean_ep_r,'k')
errorbar(f_GHz(f_bar_ind),mean_ep_r(f_bar_ind),...
         min_err_ep_r(f_bar_ind),max_err_ep_r(f_bar_ind),'LineStyle','none','Color','k')
xlabel('GHz'), title(['\epsilon_{r} VAL @ ' num2str(T) ' °C'])
%
grid off              % spegne la griglia principale
ax = gca;             % ottiene l'asse corrente
ax.YMinorGrid = 'on'; % griglia minore orizzontale
ax.XMinorGrid = 'off';
ax.YMinorTick = 'on'; % necessario per vedere la griglia minore
ax.XMinorTick = 'off';
%
axis tight, axis square
legend(['[NaCl] = 0.1mol/l @ ' num2str(T) ' °C'],'VAL (40 ml)','Location','southwest')
axis([0.5 14 47 80])
subplot(1,2,2)
plot(f/1e9,abs(imag(compPerm)).*(2*pi*f)*eps0,':g','LineWidth',2);
hold on
plot(f_GHz,mean_sigma,'k')
errorbar(f_GHz(f_bar_ind),mean_sigma(f_bar_ind),...
         min_err_sigma(f_bar_ind),max_err_sigma(f_bar_ind),'LineStyle','none','Color','k')
xlabel('GHz'), ylabel('S/m'),title(['\sigma VAL @ ' num2str(T) ' °C'])
%
grid off              % spegne la griglia principale
ax = gca;             % ottiene l'asse corrente
ax.YMinorGrid = 'on'; % griglia minore orizzontale
ax.XMinorGrid = 'off';
ax.YMinorTick = 'on'; % necessario per vedere la griglia minore
ax.XMinorTick = 'off';
%
axis tight, axis square
legend(['[NaCl] = 0.1mol/l @ ' num2str(T) ' °C'],'VAL (40 ml)','Location','northwest')
axis([0.5 14 0.5 30])
% 
clear f_GHz epsr sigm
%% MUT
% Loading data structure for CSF
load REFdata.mat
%  data reading from .prn file (works as a .txt)
n = 5;
%
[f_GHz,epsr,sigm] = Keyisight_data_reading(name_NJ,n,num_samp,eps0,1);
%[f_GHz,epsr,sigm] = Sapienza_data_reading(name_FCSF,n,num_samp,eps0,T);
%
mean_ep_r = mean(epsr);
f_bar_ind = [26;55;85;114;143;172];
max_err_ep_r = max(epsr) - mean_ep_r;
min_err_ep_r = mean_ep_r - min(epsr);
%
% max_err_ep_r_GT = GT.ep_r.max - GT.ep_r.mean;
% min_err_ep_r_GT = GT.ep_r.mean - GT.ep_r.min;
%
mean_sigma = mean(sigm);
max_err_sigma = max(sigm) - mean_sigma;
min_err_sigma = mean_sigma - min(sigm);
%
% max_err_sigma_GT = GT.sigma.max - GT.sigma.mean;
% min_err_sigma_GT = GT.sigma.mean - GT.sigma.min;
%
figure
subplot(1,2,1)
a = plot(ref_freq,ref_ep_r,'m');
hold on
b = plot(f_GHz,mean_ep_r,'k');
errorbar(f_GHz(f_bar_ind),mean_ep_r(f_bar_ind),...
         min_err_ep_r(f_bar_ind),max_err_ep_r(f_bar_ind),'LineStyle','none','Color','k')
%
grid off              % spegne la griglia principale
ax = gca;             % ottiene l'asse corrente
ax.YMinorGrid = 'on'; % griglia minore orizzontale
ax.XMinorGrid = 'off';
ax.YMinorTick = 'on'; % necessario per vedere la griglia minore
ax.XMinorTick = 'off';
%
axis tight, axis square
xlabel('GHz'), title(['\epsilon_{r} MUT @ ' num2str(T) ' °C'])
legend([a, b],'Reference','MUT (1l)')
axis([0.5 14 25 42])
%
subplot(1,2,2)
a = plot(ref_freq,ref_sigma,'m');
hold on
b = plot(f_GHz,mean_sigma,'k');
errorbar(f_GHz(f_bar_ind),mean_sigma(f_bar_ind),...
         min_err_sigma(f_bar_ind),max_err_sigma(f_bar_ind),'LineStyle','none','Color','k')
%
grid off              % spegne la griglia principale
ax = gca;             % ottiene l'asse corrente
ax.YMinorGrid = 'on'; % griglia minore orizzontale
ax.XMinorGrid = 'off';
ax.YMinorTick = 'on'; % necessario per vedere la griglia minore
ax.XMinorTick = 'off';
%
axis tight, axis square
xlabel('GHz'), ylabel('S/m'),title(['\sigma MUT @ ' num2str(T) ' °C'])
legend([a, b],'Reference','MUT (1l)','Location','northwest')
axis([0.5 14 0 12])
%
% %% Error computation
% maxerrepsr = max(abs(mean_ep_r(2:end) - ref_ep_r(2:end-1)'))
% maxerrsigma = max(abs(mean_sigma(2:end) - ref_sigma(2:end-1)'))
% % Relative accuracy
% relerr_epsr = mean(abs(mean_ep_r(2:end) - ref_ep_r(2:end-1)')...
%            ./ref_ep_r(2:end-1)')*100
% relerr_sigma = mean(abs(mean_sigma(2:end) - ref_sigma(2:end-1)')...
%            ./ref_sigma(2:end-1)')*100