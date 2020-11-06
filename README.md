# North_Taiwan_code
這是關於台灣北部非均向性分析的code,主要是資料前處理的過程:

f00_ms2sac.csh:將二進位檔案(mseed)轉成地震學專用檔(SAC)

f02_meta.csh:將地震資訊與測站資訊餵入檔案。

f03_decon.csh:去除儀器本身的影響。

f041_handpick_dataprocessing.csh:手動挑取地震波的到時。

f05_sspilt.csh:計算非均向性。

fSNR_tdomain.f90 & fssnr.csh : 計算時間域的訊噪比。

solo_new_dataprocessing.py & 2_solo_CMT_new_process.py :
資料處理的python版本
