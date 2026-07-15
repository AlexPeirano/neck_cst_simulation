function compPerm = NaCl_0to1M_5to35C(frequency, T, M)
% Cole-Cole model for 0.0-1.0M NaCl at 5.0-35.0°C
% Valid for frequencies from 130MHz to 20GHz
% Peyman et al. 2007, Complex permittivity of sodium chloride solutions

% T...teperature [°C]...5.0-35.0 °C
% M...molar concentration...0.0-1.0 M
% frequency...frequency [Hz]

permZero = 8.8541878176e-12;

permInf = 5.77-0.0274*T;
permStatWater = 10^(1.94404-(1.991e-3)*T);
tauWater = (3.745e-15)*(1+(7e-5)*(T-27.5)^2)*exp((2.2957e3)/(T+273.15));
permStat = permStatWater*(1-(3.742e-4)*T*M+0.034*M^2-0.178*M+(1.515e-4)*T-(4.929e-6)*T^2);
tau = tauWater*(1.012-(5.282e-3)*T*M+0.032*M^2-0.01*M-(1.724e-3)*T+(3.766e-5)*T^2);
sigmai = 0.174*T*M-1.582*M^2+5.923*M;
alfa = (-6.348e-4)*T*M-(5.1e-2)*M^2+(9e-2)*M;

omega = 2*pi*frequency;

compPerm = permInf+(permStat-permInf)./(1+(1i*omega*tau).^(1-alfa))+sigmai./(1i*omega*permZero);

end

