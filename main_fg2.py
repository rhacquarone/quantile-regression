# -*- coding: utf-8 -*-

from figure2_functions import *
import numpy as np
import pandas as pd
from tqdm import tqdm
import statsmodels.formula.api as smf
from scipy.linalg import sqrtm
import warnings
import os
from matplotlib import pyplot as plt
from multiprocessing import Pool
import csv
warnings.filterwarnings('ignore')

def main():
    if not os.path.exists("Data/figures2.csv"):
        np.random.seed(8)
        res_to_plot_list = []
        res0_to_plot_list = []
        res_to_plot_q_list = []
        res0_to_plot_q_list = []
        Kalpha_list = []
        Kalpha_list_q = []
        olscoeffs_list = []

        for year in ['80','90','00']:
            data = pd.read_stata('Data/census'+year+'.dta')
            # print( data)
            data_q = data
            data_q['one'] = 1.
            n = data.shape[0]
            B = 500
            b = np.round(5*n**(2/5.))
            R = np.matrix([0,1,0,0,0]).T
            R_q = data_q[["one","educ", "exper", "exper2", "black"]].multiply(data['perwt'], axis='index').mean(axis=0)
            alpha = 0.05

            taus = np.arange(1,10)/10.
            ntaus = len(taus)

            formula = 'logwk~educ+exper+exper2+black'

            V_list = []
            coeffs_list = []

            for i in tqdm(range(ntaus)):
                qr = smf.quantreg(formula, data)
                qrfit = qr.fit(q=taus[i])
                coeffs = np.array(qrfit.params)
                res = np.array(qrfit.resid)
                sigmatau = sigma(data, n, taus[i], res)
                jacobtau = jacobian(data, n, taus[i], res, alpha)
                solved_jacobian = np.linalg.inv(jacobtau)
                V = np.dot(solved_jacobian, np.dot(sigmatau, solved_jacobian))
                V_list += [V]
                coeffs_list += [coeffs]

            with Pool(4) as pool:
                K = pool.starmap(subsamplek, zip([formula]*ntaus, V_list, taus, coeffs_list, [data_q]*ntaus, [n]*ntaus, [b]*ntaus, [B]*ntaus, [R]*ntaus))
                K_q = pool.starmap(subsamplek, zip([formula]*ntaus, V_list, taus, coeffs_list, [data_q]*ntaus, [n]*ntaus, [b]*ntaus, [B]*ntaus, [R_q]*ntaus))

            K = np.array(np.matrix(K).T)
            Kmax = list(map(max,K))
            Kalpha = np.percentile(Kmax, (1-alpha)*100)

            K_q = np.array(np.matrix(K_q).T)
            Kmax_q = list(map(max,K_q))
            Kalpha_q = np.percentile(Kmax_q, (1-alpha)*100)
            
            ols = smf.ols(formula, data)
            olsfit = ols.fit()
            olscoeffs = np.dot(R.T, olsfit.params)
            olscoeffs_q = np.dot(R_q.T, olsfit.params)
            variables = np.array(olsfit.params.index)
            p = len(variables)

            taus = np.arange(2,19)/20.

            res_to_plot_list.append(table_rq_res(formula, taus=taus, data = data, alpha = alpha, R = R, n = n, sigma=sigma, jacobian = jacobian))
            res0_to_plot_list.append(table_rq_res(formula, taus=taus, data = data, alpha = alpha, R = R, n = n, sigma=sigma0, jacobian = jacobian))
            res_to_plot_q_list.append(
                table_rq_res(formula, taus=taus, data=data, alpha=alpha, R=R_q, n=n, sigma=sigma, jacobian=jacobian))
            res0_to_plot_q_list.append(
                table_rq_res(formula, taus=taus, data=data, alpha=alpha, R=R_q, n=n, sigma=sigma0, jacobian=jacobian))
            Kalpha_list.append(Kalpha)
            Kalpha_list_q.append(Kalpha_q)
            olscoeffs_list.append(olscoeffs)


        b80 = 100*np.array(res_to_plot_list[0][0].iloc[:,0])
        ub80_p = b80 + 100*Kalpha_list[0]*np.array(res_to_plot_list[0][1].iloc[:,0])
        ub80_m = b80 - 100*Kalpha_list[0]*np.array(res_to_plot_list[0][1].iloc[:,0])
        
        b90 = 100*np.array(res_to_plot_list[1][0].iloc[:,0])
        ub90_p = b90 + 100*Kalpha_list[1]*np.array(res_to_plot_list[1][1].iloc[:,0])
        ub90_m = b90 - 100*Kalpha_list[1]*np.array(res_to_plot_list[1][1].iloc[:,0])
        
        b00 = 100*np.array(res_to_plot_list[2][0].iloc[:,0])
        ub00_p = b00 + 100*Kalpha_list[2]*np.array(res_to_plot_list[2][1].iloc[:,0])
        ub00_m = b00 - 100*Kalpha_list[2]*np.array(res_to_plot_list[2][1].iloc[:,0])

        b80_bis = np.array(res_to_plot_q_list[0][0].iloc[:, 0]) - np.float(res_to_plot_q_list[0][0].iloc[8, 0])
        ub80_p_bis = b80_bis + Kalpha_list_q[0]*np.array(res_to_plot_q_list[0][1].iloc[:,0])
        ub80_m_bis = b80_bis - Kalpha_list_q[0]*np.array(res_to_plot_q_list[0][1].iloc[:,0])

        b90_bis = np.array(res_to_plot_q_list[1][0].iloc[:,0]) - np.float(res_to_plot_q_list[1][0].iloc[8,0])
        ub90_p_bis = b90_bis + Kalpha_list_q[1]*np.array(res_to_plot_q_list[1][1].iloc[:,0])
        ub90_m_bis = b90_bis - Kalpha_list_q[1]*np.array(res_to_plot_q_list[1][1].iloc[:,0])

        b00_bis = np.array(res_to_plot_q_list[2][0].iloc[:,0]) - np.float(res_to_plot_q_list[2][0].iloc[8,0])
        ub00_p_bis = b00_bis + Kalpha_list_q[2]*np.array(res_to_plot_q_list[2][1].iloc[:,0])
        ub00_m_bis = b00_bis - Kalpha_list_q[2]*np.array(res_to_plot_q_list[2][1].iloc[:,0])

        csv_df = pd.DataFrame()
        csv_df["taus"] = taus

        csv_df["b80"]= b80
        csv_df["b90"]= b90
        csv_df["b00"]= b00

        csv_df["b80_bis"]= b80_bis
        csv_df["b90_bis"]= b90_bis
        csv_df["b00_bis"]= b00_bis

        csv_df["ub80_p"]= ub80_p
        csv_df["ub90_p"]= ub90_p
        csv_df["ub00_p"]= ub00_p

        csv_df["ub80_p_bis"]= ub80_p_bis
        csv_df["ub90_p_bis"]= ub90_p_bis
        csv_df["ub00_p_bis"]= ub00_p_bis

        csv_df["ub80_m"]= ub80_m
        csv_df["ub90_m"]= ub90_m
        csv_df["ub00_m"]= ub00_m

        csv_df["ub80_m_bis"]= ub80_m_bis
        csv_df["ub90_m_bis"]= ub90_m_bis
        csv_df["ub00_m_bis"]= ub00_m_bis

        csv_df.to_csv("Data/figures2.csv")
    else :
        csv_df = pd.read_csv("Data/figures2.csv")
        taus = csv_df["taus"]

        b80 = csv_df["b80"]
        b90 = csv_df["b90"]
        b00 = csv_df["b00"]

        b80_bis = csv_df["b80_bis"]
        b90_bis = csv_df["b90_bis"]
        b00_bis = csv_df["b00_bis"]

        ub80_p = csv_df["ub80_p"]
        ub90_p = csv_df["ub90_p"]
        ub00_p = csv_df["ub00_p"]

        ub80_p_bis = csv_df["ub80_p_bis"]
        ub90_p_bis = csv_df["ub90_p_bis"]
        ub00_p_bis = csv_df["ub00_p_bis"]

        ub80_m = csv_df["ub80_m"]
        ub90_m = csv_df["ub90_m"]
        ub00_m = csv_df["ub00_m"]

        ub80_m_bis = csv_df["ub80_m_bis"]
        ub90_m_bis = csv_df["ub90_m_bis"]
        ub00_m_bis = csv_df["ub00_m_bis"]
    
    fig, (ax1) = plt.subplots()
    ax1.fill_between(taus, ub80_m, ub80_p, facecolor='silver', interpolate=True, alpha = .5)
    ax1.fill_between(taus, ub90_m, ub90_p, facecolor='black', interpolate=True, alpha = .5)
    ax1.fill_between(taus, ub00_m, ub00_p, facecolor='brown', interpolate=True, alpha = .5)
    plot80 = ax1.plot(taus, b80,'--', label = '1980', color='black')
    plot90 = ax1.plot(taus, b90,'--', label = '1990', color='black')
    plot00 = ax1.plot(taus, b00,'--', label = '2000', color='black')
    plot80_bg = ax1.fill(np.NaN, np.NaN, 'silver', alpha=0.5)
    plot90_bg = ax1.fill(np.NaN, np.NaN, 'black', alpha=0.5)
    plot00_bg = ax1.fill(np.NaN, np.NaN, 'brown', alpha=0.5)
    
    ax1.legend([(plot80_bg[0], plot80[0]), (plot90_bg[0], plot90[0]), (plot00_bg[0], plot00[0])], ['1980','1990','2000'])
    ax1.set_xlabel('Quantile Index')
    ax1.set_ylabel('Schooling Coefficients (%)')
    ax1.set_title('Schooling Coefficients')
    plt.show()

    #Second graphe

    fig, (ax1) = plt.subplots()
    plot80_bis = ax1.plot(taus, b80_bis,'--', label = '1980', color='black')
    plot90_bis = ax1.plot(taus, b90_bis,'--', label = '1990', color='black')
    plot00_bis = ax1.plot(taus, b00_bis,'--', label = '2000', color='black')
    ax1.plot(taus, [0]*len(b80_bis), color='black', lw = .5)

    ax1.fill_between(taus, ub80_m_bis, ub80_p_bis, facecolor='silver', interpolate=True, alpha = .8)
    ax1.fill_between(taus, ub90_m_bis, ub90_p_bis, facecolor='black', interpolate=True, alpha = .8)
    ax1.fill_between(taus, ub00_m_bis, ub00_p_bis, facecolor='brown', interpolate=True, alpha = .8)

    plot80_bg_bis = ax1.fill(np.NaN, np.NaN, 'silver', alpha=0.8)
    plot90_bg_bis = ax1.fill(np.NaN, np.NaN, 'black', alpha=0.8)
    plot00_bg_bis = ax1.fill(np.NaN, np.NaN, 'brown', alpha=0.8)
    ax1.legend([(plot80_bg_bis[0], plot80_bis[0]), (plot90_bg_bis[0], plot90_bis[0]), (plot00_bg_bis[0], plot00_bis[0])], ['1980','1990','2000'])
    ax1.set_xlabel('Quantile Index')
    ax1.set_ylabel('Schooling Coefficients (%)')
    ax1.set_title('CONDITIONAL QUANTILES (at covariate means)')
    plt.show()

if __name__ == '__main__':
    main()