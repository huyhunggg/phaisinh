from __future__ import annotations

import json, os, math
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Callable
import pandas as pd

VN_TZ = timezone(timedelta(hours=7))
VNSTOCK_API_KEY = os.getenv("VNSTOCK_API_KEY", "").strip()
if VNSTOCK_API_KEY:
    os.environ["VNSTOCK_API_KEY"] = VNSTOCK_API_KEY
    os.environ["VNSTOCK_TOKEN"] = VNSTOCK_API_KEY
    os.environ["VNSTOCK_KEY"] = VNSTOCK_API_KEY
    os.environ["VNSTOCK_INTERACTIVE"] = "0"
    os.environ["VNSTOCK_LANGUAGE"] = "2"

WATCHLIST = [
    "VCB",
    "BID",
    "CTG",
    "TCB",
    "MBB",
    "ACB",
    "VPB",
    "STB",
    "HDB",
    "VIB",
    "SHB",
    "LPB",
    "MSB",
    "EIB",
    "OCB",
    "TPB",
    "SSB",
    "NAB",
    "BAB",
    "BVB",
    "ABB",
    "VAB",
    "KLB",
    "PGB",
    "SSI",
    "VND",
    "HCM",
    "VCI",
    "MBS",
    "FTS",
    "BSI",
    "CTS",
    "SHS",
    "ORS",
    "AGR",
    "APG",
    "VDS",
    "BVS",
    "TVS",
    "AAS",
    "CSI",
    "EVS",
    "VIX",
    "APS",
    "WSS",
    "SBS",
    "IVS",
    "TVC",
    "VHM",
    "VIC",
    "VRE",
    "KDH",
    "NLG",
    "DXG",
    "PDR",
    "DIG",
    "CEO",
    "NVL",
    "TCH",
    "SCR",
    "HDC",
    "HDG",
    "KBC",
    "SZC",
    "BCM",
    "IDC",
    "VGC",
    "IJC",
    "CII",
    "NBB",
    "NTL",
    "SIP",
    "TIP",
    "LHG",
    "HQC",
    "ITA",
    "LDG",
    "AGG",
    "CRE",
    "DRH",
    "QCG",
    "SJS",
    "TDC",
    "D2D",
    "SZL",
    "NTC",
    "HLD",
    "HAR",
    "HPX",
    "NHA",
    "API",
    "CSC",
    "DTA",
    "FIR",
    "HPG",
    "HSG",
    "NKG",
    "TLH",
    "SMC",
    "VGS",
    "TVN",
    "TIS",
    "KSB",
    "DHA",
    "HT1",
    "BCC",
    "HOM",
    "CLH",
    "C32",
    "PLC",
    "VCS",
    "PTB",
    "ACC",
    "BTS",
    "HLY",
    "YBM",
    "FPT",
    "CMG",
    "ELC",
    "CTR",
    "VGI",
    "FOX",
    "SAM",
    "ITD",
    "ICT",
    "ONE",
    "SGT",
    "TTN",
    "VNZ",
    "DST",
    "HPT",
    "MWG",
    "FRT",
    "DGW",
    "PNJ",
    "PET",
    "PSD",
    "AST",
    "SVC",
    "HAX",
    "CTF",
    "TMT",
    "HTC",
    "COM",
    "PIT",
    "TNA",
    "BTT",
    "GAS",
    "PVD",
    "PVS",
    "PLX",
    "BSR",
    "OIL",
    "PVC",
    "PVB",
    "PVT",
    "PVP",
    "CNG",
    "PGC",
    "POW",
    "NT2",
    "QTP",
    "PPC",
    "REE",
    "GEG",
    "PC1",
    "VSH",
    "TTA",
    "SBA",
    "TMP",
    "CHP",
    "HND",
    "DGC",
    "DCM",
    "DPM",
    "CSV",
    "LAS",
    "DDV",
    "BFC",
    "GVR",
    "PHR",
    "DPR",
    "DRC",
    "BMP",
    "NTP",
    "AAA",
    "APH",
    "DHC",
    "GIL",
    "TNG",
    "MSH",
    "TCM",
    "STK",
    "ADS",
    "HII",
    "PLP",
    "RDP",
    "DAG",
    "VTZ",
    "CSM",
    "SRC",
    "VNM",
    "MSN",
    "MCH",
    "SAB",
    "KDC",
    "QNS",
    "DBC",
    "BAF",
    "PAN",
    "TAR",
    "ANV",
    "VHC",
    "IDI",
    "ASM",
    "HAG",
    "HNG",
    "SBT",
    "LSS",
    "SLS",
    "MML",
    "VOC",
    "NAF",
    "HSL",
    "AFX",
    "LTG",
    "MPC",
    "FMC",
    "ACL",
    "CMX",
    "KHS",
    "HAP",
    "HHC",
    "BBC",
    "VLC",
    "VSN",
    "GMD",
    "HAH",
    "VSC",
    "SGP",
    "PHP",
    "VOS",
    "VTO",
    "SKG",
    "VTP",
    "TMS",
    "SFI",
    "DVP",
    "PDN",
    "CDN",
    "SCS",
    "NCT",
    "GSP",
    "VIP",
    "VNS",
    "TCO",
    "TCL",
    "PCT",
    "TJC",
    "VJC",
    "HVN",
    "ACV",
    "SAS",
    "CIA",
    "MAS",
    "SGN",
    "NCS",
    "CTD",
    "HBC",
    "FCN",
    "HHV",
    "LCG",
    "C4G",
    "VCG",
    "DPG",
    "HUT",
    "PHC",
    "HTN",
    "C47",
    "G36",
    "TCD",
    "L14",
    "MST",
    "DHG",
    "IMP",
    "TRA",
    "DCL",
    "DBD",
    "DMC",
    "TNH",
    "JVC",
    "DVN",
    "AMV",
    "DP3",
    "OPC",
    "PME",
    "VMD",
    "FIT",
    "BVH",
    "BMI",
    "PVI",
    "BIC",
    "MIG",
    "ABI",
    "PTI",
    "PRE",
    "VNR",
    "BWE",
    "TDM",
    "SJD",
    "TBC",
    "RAL",
    "PAC",
    "SAV",
    "GDT",
    "TCT",
    "VEA",
    "HHS",
    "NHH"
]
NAMES = {
    "VCB": "Vietcombank",
    "BID": "BIDV",
    "CTG": "VietinBank",
    "TCB": "Techcombank",
    "MBB": "Ngân hàng Quân đội",
    "ACB": "Ngân hàng Á Châu",
    "VPB": "VPB",
    "STB": "STB",
    "HDB": "HDB",
    "VIB": "VIB",
    "SHB": "SHB",
    "LPB": "LPB",
    "MSB": "MSB",
    "EIB": "EIB",
    "OCB": "OCB",
    "TPB": "TPB",
    "SSB": "SSB",
    "NAB": "NAB",
    "BAB": "BAB",
    "BVB": "BVB",
    "ABB": "ABB",
    "VAB": "VAB",
    "KLB": "KLB",
    "PGB": "PGB",
    "SSI": "Chứng khoán SSI",
    "VND": "VNDIRECT",
    "HCM": "Chứng khoán HSC",
    "VCI": "Vietcap",
    "MBS": "Chứng khoán MB",
    "FTS": "FTS",
    "BSI": "BSI",
    "CTS": "CTS",
    "SHS": "SHS",
    "ORS": "ORS",
    "AGR": "AGR",
    "APG": "APG",
    "VDS": "VDS",
    "BVS": "BVS",
    "TVS": "TVS",
    "AAS": "AAS",
    "CSI": "CSI",
    "EVS": "EVS",
    "VIX": "VIX",
    "APS": "APS",
    "WSS": "WSS",
    "SBS": "SBS",
    "IVS": "IVS",
    "TVC": "TVC",
    "VHM": "Vinhomes",
    "VIC": "Vingroup",
    "VRE": "VRE",
    "KDH": "KDH",
    "NLG": "NLG",
    "DXG": "DXG",
    "PDR": "PDR",
    "DIG": "DIG",
    "CEO": "CEO",
    "NVL": "NVL",
    "TCH": "TCH",
    "SCR": "SCR",
    "HDC": "HDC",
    "HDG": "HDG",
    "KBC": "KBC",
    "SZC": "SZC",
    "BCM": "BCM",
    "IDC": "IDC",
    "VGC": "VGC",
    "IJC": "IJC",
    "CII": "CII",
    "NBB": "NBB",
    "NTL": "NTL",
    "SIP": "SIP",
    "TIP": "TIP",
    "LHG": "LHG",
    "HQC": "HQC",
    "ITA": "ITA",
    "LDG": "LDG",
    "AGG": "AGG",
    "CRE": "CRE",
    "DRH": "DRH",
    "QCG": "QCG",
    "SJS": "SJS",
    "TDC": "TDC",
    "D2D": "D2D",
    "SZL": "SZL",
    "NTC": "NTC",
    "HLD": "HLD",
    "HAR": "HAR",
    "HPX": "HPX",
    "NHA": "NHA",
    "API": "API",
    "CSC": "CSC",
    "DTA": "DTA",
    "FIR": "FIR",
    "HPG": "Hòa Phát",
    "HSG": "HSG",
    "NKG": "NKG",
    "TLH": "TLH",
    "SMC": "SMC",
    "VGS": "VGS",
    "TVN": "TVN",
    "TIS": "TIS",
    "KSB": "KSB",
    "DHA": "DHA",
    "HT1": "HT1",
    "BCC": "BCC",
    "HOM": "HOM",
    "CLH": "CLH",
    "C32": "C32",
    "PLC": "PLC",
    "VCS": "VCS",
    "PTB": "PTB",
    "ACC": "ACC",
    "BTS": "BTS",
    "HLY": "HLY",
    "YBM": "YBM",
    "FPT": "FPT Corp",
    "CMG": "CMG",
    "ELC": "ELC",
    "CTR": "CTR",
    "VGI": "VGI",
    "FOX": "FOX",
    "SAM": "SAM",
    "ITD": "ITD",
    "ICT": "ICT",
    "ONE": "ONE",
    "SGT": "SGT",
    "TTN": "TTN",
    "VNZ": "VNZ",
    "DST": "DST",
    "HPT": "HPT",
    "MWG": "Thế Giới Di Động",
    "FRT": "FRT",
    "DGW": "DGW",
    "PNJ": "PNJ",
    "PET": "PET",
    "PSD": "PSD",
    "AST": "AST",
    "SVC": "SVC",
    "HAX": "HAX",
    "CTF": "CTF",
    "TMT": "TMT",
    "HTC": "HTC",
    "COM": "COM",
    "PIT": "PIT",
    "TNA": "TNA",
    "BTT": "BTT",
    "GAS": "PV GAS",
    "PVD": "PV Drilling",
    "PVS": "PTSC",
    "PLX": "PLX",
    "BSR": "BSR",
    "OIL": "OIL",
    "PVC": "PVC",
    "PVB": "PVB",
    "PVT": "PVT",
    "PVP": "PVP",
    "CNG": "CNG",
    "PGC": "PGC",
    "POW": "POW",
    "NT2": "NT2",
    "QTP": "QTP",
    "PPC": "PPC",
    "REE": "REE",
    "GEG": "GEG",
    "PC1": "PC1",
    "VSH": "VSH",
    "TTA": "TTA",
    "SBA": "SBA",
    "TMP": "TMP",
    "CHP": "CHP",
    "HND": "HND",
    "DGC": "Hóa chất Đức Giang",
    "DCM": "DCM",
    "DPM": "DPM",
    "CSV": "CSV",
    "LAS": "LAS",
    "DDV": "DDV",
    "BFC": "BFC",
    "GVR": "GVR",
    "PHR": "PHR",
    "DPR": "DPR",
    "DRC": "DRC",
    "BMP": "BMP",
    "NTP": "NTP",
    "AAA": "AAA",
    "APH": "APH",
    "DHC": "DHC",
    "GIL": "GIL",
    "TNG": "TNG",
    "MSH": "MSH",
    "TCM": "TCM",
    "STK": "STK",
    "ADS": "ADS",
    "HII": "HII",
    "PLP": "PLP",
    "RDP": "RDP",
    "DAG": "DAG",
    "VTZ": "VTZ",
    "CSM": "CSM",
    "SRC": "SRC",
    "VNM": "Vinamilk",
    "MSN": "Masan",
    "MCH": "MCH",
    "SAB": "SAB",
    "KDC": "KDC",
    "QNS": "QNS",
    "DBC": "DBC",
    "BAF": "BAF",
    "PAN": "PAN",
    "TAR": "TAR",
    "ANV": "ANV",
    "VHC": "VHC",
    "IDI": "IDI",
    "ASM": "ASM",
    "HAG": "HAG",
    "HNG": "HNG",
    "SBT": "SBT",
    "LSS": "LSS",
    "SLS": "SLS",
    "MML": "MML",
    "VOC": "VOC",
    "NAF": "NAF",
    "HSL": "HSL",
    "AFX": "AFX",
    "LTG": "LTG",
    "MPC": "MPC",
    "FMC": "FMC",
    "ACL": "ACL",
    "CMX": "CMX",
    "KHS": "KHS",
    "HAP": "HAP",
    "HHC": "HHC",
    "BBC": "BBC",
    "VLC": "VLC",
    "VSN": "VSN",
    "GMD": "Gemadept",
    "HAH": "HAH",
    "VSC": "VSC",
    "SGP": "SGP",
    "PHP": "PHP",
    "VOS": "VOS",
    "VTO": "VTO",
    "SKG": "SKG",
    "VTP": "VTP",
    "TMS": "TMS",
    "SFI": "SFI",
    "DVP": "DVP",
    "PDN": "PDN",
    "CDN": "CDN",
    "SCS": "SCS",
    "NCT": "NCT",
    "GSP": "GSP",
    "VIP": "VIP",
    "VNS": "VNS",
    "TCO": "TCO",
    "TCL": "TCL",
    "PCT": "PCT",
    "TJC": "TJC",
    "VJC": "Vietjet",
    "HVN": "Vietnam Airlines",
    "ACV": "Cảng HKVN",
    "SAS": "SAS",
    "CIA": "CIA",
    "MAS": "MAS",
    "SGN": "SGN",
    "NCS": "NCS",
    "CTD": "CTD",
    "HBC": "HBC",
    "FCN": "FCN",
    "HHV": "HHV",
    "LCG": "LCG",
    "C4G": "C4G",
    "VCG": "VCG",
    "DPG": "DPG",
    "HUT": "HUT",
    "PHC": "PHC",
    "HTN": "HTN",
    "C47": "C47",
    "G36": "G36",
    "TCD": "TCD",
    "L14": "L14",
    "MST": "MST",
    "DHG": "DHG",
    "IMP": "IMP",
    "TRA": "TRA",
    "DCL": "DCL",
    "DBD": "DBD",
    "DMC": "DMC",
    "TNH": "TNH",
    "JVC": "JVC",
    "DVN": "DVN",
    "AMV": "AMV",
    "DP3": "DP3",
    "OPC": "OPC",
    "PME": "PME",
    "VMD": "VMD",
    "FIT": "FIT",
    "BVH": "BVH",
    "BMI": "BMI",
    "PVI": "PVI",
    "BIC": "BIC",
    "MIG": "MIG",
    "ABI": "ABI",
    "PTI": "PTI",
    "PRE": "PRE",
    "VNR": "VNR",
    "BWE": "BWE",
    "TDM": "TDM",
    "SJD": "SJD",
    "TBC": "TBC",
    "RAL": "RAL",
    "PAC": "PAC",
    "SAV": "SAV",
    "GDT": "GDT",
    "TCT": "TCT",
    "VEA": "VEA",
    "HHS": "HHS",
    "NHH": "NHH"
}
SECTORS = {
    "VCB": "Ngân hàng",
    "BID": "Ngân hàng",
    "CTG": "Ngân hàng",
    "TCB": "Ngân hàng",
    "MBB": "Ngân hàng",
    "ACB": "Ngân hàng",
    "VPB": "Ngân hàng",
    "STB": "Ngân hàng",
    "HDB": "Ngân hàng",
    "VIB": "Ngân hàng",
    "SHB": "Ngân hàng",
    "LPB": "Ngân hàng",
    "MSB": "Ngân hàng",
    "EIB": "Ngân hàng",
    "OCB": "Ngân hàng",
    "TPB": "Ngân hàng",
    "SSB": "Ngân hàng",
    "NAB": "Ngân hàng",
    "BAB": "Ngân hàng",
    "BVB": "Ngân hàng",
    "ABB": "Ngân hàng",
    "VAB": "Ngân hàng",
    "KLB": "Ngân hàng",
    "PGB": "Ngân hàng",
    "SSI": "Chứng khoán",
    "VND": "Chứng khoán",
    "HCM": "Chứng khoán",
    "VCI": "Chứng khoán",
    "MBS": "Chứng khoán",
    "FTS": "Chứng khoán",
    "BSI": "Chứng khoán",
    "CTS": "Chứng khoán",
    "SHS": "Chứng khoán",
    "ORS": "Chứng khoán",
    "AGR": "Chứng khoán",
    "APG": "Chứng khoán",
    "VDS": "Chứng khoán",
    "BVS": "Chứng khoán",
    "TVS": "Chứng khoán",
    "AAS": "Chứng khoán",
    "CSI": "Chứng khoán",
    "EVS": "Chứng khoán",
    "VIX": "Chứng khoán",
    "APS": "Chứng khoán",
    "WSS": "Chứng khoán",
    "SBS": "Chứng khoán",
    "IVS": "Chứng khoán",
    "TVC": "Chứng khoán",
    "VHM": "Bất động sản / KCN",
    "VIC": "Bất động sản / KCN",
    "VRE": "Bất động sản / KCN",
    "KDH": "Bất động sản / KCN",
    "NLG": "Bất động sản / KCN",
    "DXG": "Bất động sản / KCN",
    "PDR": "Bất động sản / KCN",
    "DIG": "Bất động sản / KCN",
    "CEO": "Bất động sản / KCN",
    "NVL": "Bất động sản / KCN",
    "TCH": "Bất động sản / KCN",
    "SCR": "Bất động sản / KCN",
    "HDC": "Bất động sản / KCN",
    "HDG": "Dầu khí / Năng lượng",
    "KBC": "Bất động sản / KCN",
    "SZC": "Bất động sản / KCN",
    "BCM": "Bất động sản / KCN",
    "IDC": "Bất động sản / KCN",
    "VGC": "Bất động sản / KCN",
    "IJC": "Bất động sản / KCN",
    "CII": "Bất động sản / KCN",
    "NBB": "Bất động sản / KCN",
    "NTL": "Bất động sản / KCN",
    "SIP": "Bất động sản / KCN",
    "TIP": "Bất động sản / KCN",
    "LHG": "Bất động sản / KCN",
    "HQC": "Bất động sản / KCN",
    "ITA": "Bất động sản / KCN",
    "LDG": "Bất động sản / KCN",
    "AGG": "Bất động sản / KCN",
    "CRE": "Bất động sản / KCN",
    "DRH": "Bất động sản / KCN",
    "QCG": "Bất động sản / KCN",
    "SJS": "Bất động sản / KCN",
    "TDC": "Bất động sản / KCN",
    "D2D": "Bất động sản / KCN",
    "SZL": "Bất động sản / KCN",
    "NTC": "Bất động sản / KCN",
    "HLD": "Bất động sản / KCN",
    "HAR": "Bất động sản / KCN",
    "HPX": "Bất động sản / KCN",
    "NHA": "Bất động sản / KCN",
    "API": "Bất động sản / KCN",
    "CSC": "Bất động sản / KCN",
    "DTA": "Bất động sản / KCN",
    "FIR": "Bất động sản / KCN",
    "HPG": "Thép / Vật liệu",
    "HSG": "Thép / Vật liệu",
    "NKG": "Thép / Vật liệu",
    "TLH": "Thép / Vật liệu",
    "SMC": "Thép / Vật liệu",
    "VGS": "Thép / Vật liệu",
    "TVN": "Thép / Vật liệu",
    "TIS": "Thép / Vật liệu",
    "KSB": "Thép / Vật liệu",
    "DHA": "Thép / Vật liệu",
    "HT1": "Thép / Vật liệu",
    "BCC": "Thép / Vật liệu",
    "HOM": "Thép / Vật liệu",
    "CLH": "Thép / Vật liệu",
    "C32": "Thép / Vật liệu",
    "PLC": "Thép / Vật liệu",
    "VCS": "Thép / Vật liệu",
    "PTB": "Thép / Vật liệu",
    "ACC": "Thép / Vật liệu",
    "BTS": "Thép / Vật liệu",
    "HLY": "Thép / Vật liệu",
    "YBM": "Thép / Vật liệu",
    "FPT": "Công nghệ / Viễn thông",
    "CMG": "Công nghệ / Viễn thông",
    "ELC": "Công nghệ / Viễn thông",
    "CTR": "Công nghệ / Viễn thông",
    "VGI": "Công nghệ / Viễn thông",
    "FOX": "Công nghệ / Viễn thông",
    "SAM": "Công nghệ / Viễn thông",
    "ITD": "Công nghệ / Viễn thông",
    "ICT": "Công nghệ / Viễn thông",
    "ONE": "Công nghệ / Viễn thông",
    "SGT": "Công nghệ / Viễn thông",
    "TTN": "Công nghệ / Viễn thông",
    "VNZ": "Công nghệ / Viễn thông",
    "DST": "Công nghệ / Viễn thông",
    "HPT": "Công nghệ / Viễn thông",
    "MWG": "Bán lẻ / Phân phối",
    "FRT": "Bán lẻ / Phân phối",
    "DGW": "Bán lẻ / Phân phối",
    "PNJ": "Bán lẻ / Phân phối",
    "PET": "Bán lẻ / Phân phối",
    "PSD": "Bán lẻ / Phân phối",
    "AST": "Bán lẻ / Phân phối",
    "SVC": "Bán lẻ / Phân phối",
    "HAX": "Bán lẻ / Phân phối",
    "CTF": "Bán lẻ / Phân phối",
    "TMT": "Bán lẻ / Phân phối",
    "HTC": "Bán lẻ / Phân phối",
    "COM": "Bán lẻ / Phân phối",
    "PIT": "Bán lẻ / Phân phối",
    "TNA": "Bán lẻ / Phân phối",
    "BTT": "Bán lẻ / Phân phối",
    "GAS": "Dầu khí / Năng lượng",
    "PVD": "Dầu khí / Năng lượng",
    "PVS": "Dầu khí / Năng lượng",
    "PLX": "Dầu khí / Năng lượng",
    "BSR": "Dầu khí / Năng lượng",
    "OIL": "Dầu khí / Năng lượng",
    "PVC": "Dầu khí / Năng lượng",
    "PVB": "Dầu khí / Năng lượng",
    "PVT": "Dầu khí / Năng lượng",
    "PVP": "Dầu khí / Năng lượng",
    "CNG": "Dầu khí / Năng lượng",
    "PGC": "Dầu khí / Năng lượng",
    "POW": "Dầu khí / Năng lượng",
    "NT2": "Dầu khí / Năng lượng",
    "QTP": "Dầu khí / Năng lượng",
    "PPC": "Dầu khí / Năng lượng",
    "REE": "Dầu khí / Năng lượng",
    "GEG": "Dầu khí / Năng lượng",
    "PC1": "Dầu khí / Năng lượng",
    "VSH": "Dầu khí / Năng lượng",
    "TTA": "Dầu khí / Năng lượng",
    "SBA": "Dầu khí / Năng lượng",
    "TMP": "Dầu khí / Năng lượng",
    "CHP": "Dầu khí / Năng lượng",
    "HND": "Dầu khí / Năng lượng",
    "DGC": "Hóa chất / Vật liệu / Dệt may",
    "DCM": "Hóa chất / Vật liệu / Dệt may",
    "DPM": "Hóa chất / Vật liệu / Dệt may",
    "CSV": "Hóa chất / Vật liệu / Dệt may",
    "LAS": "Hóa chất / Vật liệu / Dệt may",
    "DDV": "Hóa chất / Vật liệu / Dệt may",
    "BFC": "Hóa chất / Vật liệu / Dệt may",
    "GVR": "Hóa chất / Vật liệu / Dệt may",
    "PHR": "Hóa chất / Vật liệu / Dệt may",
    "DPR": "Hóa chất / Vật liệu / Dệt may",
    "DRC": "Hóa chất / Vật liệu / Dệt may",
    "BMP": "Hóa chất / Vật liệu / Dệt may",
    "NTP": "Hóa chất / Vật liệu / Dệt may",
    "AAA": "Hóa chất / Vật liệu / Dệt may",
    "APH": "Hóa chất / Vật liệu / Dệt may",
    "DHC": "Hóa chất / Vật liệu / Dệt may",
    "GIL": "Hóa chất / Vật liệu / Dệt may",
    "TNG": "Hóa chất / Vật liệu / Dệt may",
    "MSH": "Hóa chất / Vật liệu / Dệt may",
    "TCM": "Hóa chất / Vật liệu / Dệt may",
    "STK": "Hóa chất / Vật liệu / Dệt may",
    "ADS": "Hóa chất / Vật liệu / Dệt may",
    "HII": "Hóa chất / Vật liệu / Dệt may",
    "PLP": "Hóa chất / Vật liệu / Dệt may",
    "RDP": "Hóa chất / Vật liệu / Dệt may",
    "DAG": "Hóa chất / Vật liệu / Dệt may",
    "VTZ": "Hóa chất / Vật liệu / Dệt may",
    "CSM": "Hóa chất / Vật liệu / Dệt may",
    "SRC": "Hóa chất / Vật liệu / Dệt may",
    "VNM": "Tiêu dùng / Nông nghiệp",
    "MSN": "Tiêu dùng / Nông nghiệp",
    "MCH": "Tiêu dùng / Nông nghiệp",
    "SAB": "Tiêu dùng / Nông nghiệp",
    "KDC": "Tiêu dùng / Nông nghiệp",
    "QNS": "Tiêu dùng / Nông nghiệp",
    "DBC": "Tiêu dùng / Nông nghiệp",
    "BAF": "Tiêu dùng / Nông nghiệp",
    "PAN": "Tiêu dùng / Nông nghiệp",
    "TAR": "Tiêu dùng / Nông nghiệp",
    "ANV": "Tiêu dùng / Nông nghiệp",
    "VHC": "Tiêu dùng / Nông nghiệp",
    "IDI": "Tiêu dùng / Nông nghiệp",
    "ASM": "Tiêu dùng / Nông nghiệp",
    "HAG": "Tiêu dùng / Nông nghiệp",
    "HNG": "Tiêu dùng / Nông nghiệp",
    "SBT": "Tiêu dùng / Nông nghiệp",
    "LSS": "Tiêu dùng / Nông nghiệp",
    "SLS": "Tiêu dùng / Nông nghiệp",
    "MML": "Tiêu dùng / Nông nghiệp",
    "VOC": "Tiêu dùng / Nông nghiệp",
    "NAF": "Tiêu dùng / Nông nghiệp",
    "HSL": "Tiêu dùng / Nông nghiệp",
    "AFX": "Tiêu dùng / Nông nghiệp",
    "LTG": "Tiêu dùng / Nông nghiệp",
    "MPC": "Tiêu dùng / Nông nghiệp",
    "FMC": "Tiêu dùng / Nông nghiệp",
    "ACL": "Tiêu dùng / Nông nghiệp",
    "CMX": "Tiêu dùng / Nông nghiệp",
    "KHS": "Tiêu dùng / Nông nghiệp",
    "HAP": "Tiêu dùng / Nông nghiệp",
    "HHC": "Tiêu dùng / Nông nghiệp",
    "BBC": "Tiêu dùng / Nông nghiệp",
    "VLC": "Tiêu dùng / Nông nghiệp",
    "VSN": "Tiêu dùng / Nông nghiệp",
    "GMD": "Logistics / Vận tải",
    "HAH": "Logistics / Vận tải",
    "VSC": "Logistics / Vận tải",
    "SGP": "Logistics / Vận tải",
    "PHP": "Logistics / Vận tải",
    "VOS": "Logistics / Vận tải",
    "VTO": "Logistics / Vận tải",
    "SKG": "Logistics / Vận tải",
    "VTP": "Logistics / Vận tải",
    "TMS": "Logistics / Vận tải",
    "SFI": "Logistics / Vận tải",
    "DVP": "Logistics / Vận tải",
    "PDN": "Logistics / Vận tải",
    "CDN": "Logistics / Vận tải",
    "SCS": "Logistics / Vận tải",
    "NCT": "Logistics / Vận tải",
    "GSP": "Logistics / Vận tải",
    "VIP": "Logistics / Vận tải",
    "VNS": "Logistics / Vận tải",
    "TCO": "Logistics / Vận tải",
    "TCL": "Logistics / Vận tải",
    "PCT": "Logistics / Vận tải",
    "TJC": "Logistics / Vận tải",
    "VJC": "Hàng không",
    "HVN": "Hàng không",
    "ACV": "Hàng không",
    "SAS": "Hàng không",
    "CIA": "Hàng không",
    "MAS": "Hàng không",
    "SGN": "Hàng không",
    "NCS": "Hàng không",
    "CTD": "Xây dựng / Hạ tầng",
    "HBC": "Xây dựng / Hạ tầng",
    "FCN": "Xây dựng / Hạ tầng",
    "HHV": "Xây dựng / Hạ tầng",
    "LCG": "Xây dựng / Hạ tầng",
    "C4G": "Xây dựng / Hạ tầng",
    "VCG": "Xây dựng / Hạ tầng",
    "DPG": "Xây dựng / Hạ tầng",
    "HUT": "Xây dựng / Hạ tầng",
    "PHC": "Xây dựng / Hạ tầng",
    "HTN": "Xây dựng / Hạ tầng",
    "C47": "Xây dựng / Hạ tầng",
    "G36": "Xây dựng / Hạ tầng",
    "TCD": "Xây dựng / Hạ tầng",
    "L14": "Xây dựng / Hạ tầng",
    "MST": "Xây dựng / Hạ tầng",
    "DHG": "Dược / Y tế",
    "IMP": "Dược / Y tế",
    "TRA": "Dược / Y tế",
    "DCL": "Dược / Y tế",
    "DBD": "Dược / Y tế",
    "DMC": "Dược / Y tế",
    "TNH": "Dược / Y tế",
    "JVC": "Dược / Y tế",
    "DVN": "Dược / Y tế",
    "AMV": "Dược / Y tế",
    "DP3": "Dược / Y tế",
    "OPC": "Dược / Y tế",
    "PME": "Dược / Y tế",
    "VMD": "Dược / Y tế",
    "FIT": "Dược / Y tế",
    "BVH": "Bảo hiểm",
    "BMI": "Bảo hiểm",
    "PVI": "Bảo hiểm",
    "BIC": "Bảo hiểm",
    "MIG": "Bảo hiểm",
    "ABI": "Bảo hiểm",
    "PTI": "Bảo hiểm",
    "PRE": "Bảo hiểm",
    "VNR": "Bảo hiểm",
    "BWE": "Khác",
    "TDM": "Khác",
    "SJD": "Khác",
    "TBC": "Khác",
    "RAL": "Khác",
    "PAC": "Khác",
    "SAV": "Khác",
    "GDT": "Khác",
    "TCT": "Khác",
    "VEA": "Khác",
    "HHS": "Khác",
    "NHH": "Khác"
}

END_DATE = datetime.now(VN_TZ).strftime("%Y-%m-%d")
START_DATE = (datetime.now(VN_TZ) - timedelta(days=520)).strftime("%Y-%m-%d")

def safe_float(x, ndigits=2):
    try:
        if x is None or pd.isna(x): return None
        return round(float(x), ndigits)
    except Exception: return None

def normalize_columns(df):
    df=df.copy()
    lower={str(c).lower().strip():c for c in df.columns}
    aliases={"time":["time","date","tradingdate","trading_date"],"open":["open","openprice"],"high":["high","highestprice"],"low":["low","lowestprice"],"close":["close","closeprice","matchprice","price"],"volume":["volume","nmvolume","total_volume","matchingvolume"]}
    rename={}
    for target,keys in aliases.items():
        for k in keys:
            if k in lower:
                rename[lower[k]]=target; break
    df=df.rename(columns=rename)
    if "time" not in df.columns: df["time"]=range(len(df))
    if "close" not in df.columns: raise ValueError(f"Missing close column. Columns={list(df.columns)}")
    for col in ["open","high","low"]:
        if col not in df.columns: df[col]=df["close"]
    if "volume" not in df.columns: df["volume"]=0
    for col in ["open","high","low","close","volume"]:
        df[col]=pd.to_numeric(df[col], errors="coerce")
    df["volume"]=df["volume"].fillna(0)
    df=df.dropna(subset=["close"]).reset_index(drop=True)
    if len(df) and df["close"].median()<1000:
        for col in ["open","high","low","close"]: df[col]*=1000
    return df

def rsi(series, period=14):
    delta=series.diff(); gain=delta.clip(lower=0).rolling(period).mean(); loss=(-delta.clip(upper=0)).rolling(period).mean()
    rs=gain/loss.replace(0,pd.NA); return 100-(100/(1+rs))

def macd(series):
    ema12=series.ewm(span=12,adjust=False).mean(); ema26=series.ewm(span=26,adjust=False).mean()
    line=ema12-ema26; signal=line.ewm(span=9,adjust=False).mean(); return line, signal, line-signal

def atr(df, period=14):
    high_low=df["high"]-df["low"]; high_close=(df["high"]-df["close"].shift()).abs(); low_close=(df["low"]-df["close"].shift()).abs()
    tr=pd.concat([high_low,high_close,low_close],axis=1).max(axis=1)
    return tr.rolling(period).mean()

def fetch_history(symbol):
    attempts=[]
    try:
        from vnstock import Quote
        for src in ["VCI","KBS","TCBS","VND","vci","kbs","tcbs","vnd"]:
            attempts.append((f"Quote/{src}", lambda src=src: Quote(symbol=symbol, source=src).history(start=START_DATE,end=END_DATE,interval="1D")))
    except Exception: pass
    try:
        from vnstock import Vnstock
        for src in ["VCI","KBS","TCBS","vci","kbs","tcbs"]:
            attempts.append((f"Vnstock/{src}", lambda src=src: Vnstock().stock(symbol=symbol, source=src).quote.history(start=START_DATE,end=END_DATE,interval="1D")))
    except Exception: pass
    errors=[]
    for name,fn in attempts:
        try:
            df=normalize_columns(fn())
            if len(df)>=80: return df,name
            errors.append(f"{name} too few rows {len(df)}")
        except Exception as e: errors.append(f"{name}: {type(e).__name__} {e}")
    raise RuntimeError(" | ".join(errors[:6]) or "No fetch method")

def add_indicators(df):
    c=df["close"]
    for p in [5,10,20,50,100,200]:
        df[f"ma{p}"]=c.rolling(p).mean()
    df["ema12"]=c.ewm(span=12,adjust=False).mean(); df["ema26"]=c.ewm(span=26,adjust=False).mean()
    df["macd"],df["macd_signal"],df["macd_hist"]=macd(c)
    df["rsi14"]=rsi(c); df["vol_ma20"]=df["volume"].rolling(20).mean(); df["vol_ratio"]=df["volume"]/df["vol_ma20"]
    df["value_traded"]=df["close"]*df["volume"]; df["value_ma20"]=df["value_traded"].rolling(20).mean()
    df["high20_prev"]=df["high"].rolling(20).max().shift(1); df["low20_prev"]=df["low"].rolling(20).min().shift(1)
    df["high50_prev"]=df["high"].rolling(50).max().shift(1); df["low50_prev"]=df["low"].rolling(50).min().shift(1)
    df["atr14"]=atr(df); df["distance_ma20"]=(df["close"]-df["ma20"])/df["ma20"]
    return df

def levels(df, close):
    recent=df.tail(80)
    highs=[]; lows=[]
    for i in range(2, len(recent)-2):
        row=recent.iloc[i]
        if row["high"]>recent.iloc[i-1]["high"] and row["high"]>recent.iloc[i-2]["high"] and row["high"]>recent.iloc[i+1]["high"] and row["high"]>recent.iloc[i+2]["high"]:
            highs.append(float(row["high"]))
        if row["low"]<recent.iloc[i-1]["low"] and row["low"]<recent.iloc[i-2]["low"] and row["low"]<recent.iloc[i+1]["low"] and row["low"]<recent.iloc[i+2]["low"]:
            lows.append(float(row["low"]))
    support_candidates=[x for x in lows if x<close]
    resistance_candidates=[x for x in highs if x>close]
    support_near=max(support_candidates) if support_candidates else float(recent["low"].tail(20).min())
    resistance_near=min(resistance_candidates) if resistance_candidates else float(recent["high"].tail(20).max())
    support_key=float(recent["low"].tail(50).min())
    breakout_level=float(recent["high"].tail(20).max())
    return {"support_near":safe_float(support_near,0),"support_key":safe_float(support_key,0),"resistance_near":safe_float(resistance_near,0),"breakout_level":safe_float(breakout_level,0),"target_zone":[safe_float(resistance_near*1.06,0),safe_float(resistance_near*1.15,0)]}

def classify_and_score(symbol, df, bench_ret20=None, bench_ret60=None, bench_ret120=None):
    df=add_indicators(df)
    latest=df.iloc[-1]; prev=df.iloc[-2]
    c=float(latest["close"])
    # returns
    ret20=(c/float(df.iloc[-21]["close"])-1) if len(df)>21 else 0
    ret60=(c/float(df.iloc[-61]["close"])-1) if len(df)>61 else 0
    ret120=(c/float(df.iloc[-121]["close"])-1) if len(df)>121 else 0
    rs20=ret20-(bench_ret20 or 0); rs60=ret60-(bench_ret60 or 0); rs120=ret120-(bench_ret120 or 0)
    # candle
    rng=max(1,float(latest["high"]-latest["low"])); body=abs(float(latest["close"]-latest["open"]))
    upper=float(latest["high"]-max(latest["open"],latest["close"])); lower=float(min(latest["open"],latest["close"])-latest["low"])
    upper_wick_long=upper>0.4*rng; lower_wick_long=lower>0.4*rng
    close_near_high=float(latest["close"])>float(latest["low"])+0.7*rng
    # flags
    breakout=bool(latest["close"]>latest["high20_prev"] and latest["vol_ratio"]>=1.5 and latest["rsi14"]>55 and latest["macd"]>latest["macd_signal"] and latest["close"]>latest["ma20"])
    breakdown=bool(latest["close"]<latest["low20_prev"] and latest["vol_ratio"]>=1.5 and latest["rsi14"]<45 and latest["macd"]<latest["macd_signal"] and latest["close"]<latest["ma20"])
    false_breakout=bool(latest["high"]>latest["high20_prev"] and latest["close"]<latest["high20_prev"] and upper_wick_long and latest["vol_ratio"]>=1.5)
    overextended=bool(latest["distance_ma20"]>0.15 or (latest["distance_ma20"]>0.12 and latest["rsi14"]>70))
    reclaim=bool(latest["close"]>latest["ma20"] and latest["close"]>latest["ma50"] and (prev["close"]<=prev["ma20"] or prev["close"]<=prev["ma50"]) and latest["rsi14"]>50)
    pullback=bool(latest["close"]>latest["ma50"] and latest["ma20"]>latest["ma50"] and -0.02<=latest["distance_ma20"]<=0.05 and latest["rsi14"]>50)
    price_range=(df.tail(20)["high"].max()-df.tail(20)["low"].min())/c
    vol_now=df.tail(5)["volume"].mean(); vol_before=df.tail(20).head(5)["volume"].mean()
    accumulation=bool(price_range<0.12 and vol_now<vol_before and latest["close"]>latest["ma50"] and 45<=latest["rsi14"]<=60)
    avoid=bool(latest["close"]<latest["low50_prev"] and latest["close"]<latest["ma20"] and latest["close"]<latest["ma50"] and latest["rsi14"]<40 and latest["macd"]<0 and rs20<0)
    # scores
    trend=0
    for ma in ["ma20","ma50","ma100"]:
        if latest["close"]>latest[ma]: trend+=5
    if latest["ma20"]>latest["ma50"]: trend+=5
    if latest["ma50"]>latest["ma100"]: trend+=5
    if latest["ma20"]>df.iloc[-6]["ma20"]: trend+=5
    momentum=0
    if latest["rsi14"]>50: momentum+=5
    if latest["rsi14"]>60: momentum+=5
    if latest["macd"]>latest["macd_signal"]: momentum+=5
    if latest["macd"]>0: momentum+=5
    volume=0
    if latest["volume"]>latest["vol_ma20"] and latest["close"]>latest["open"]: volume+=5
    if latest["vol_ratio"]>=1.5 and latest["close"]>latest["open"]: volume+=10
    if breakout: volume+=5
    position=0
    if latest["close"]>=latest["high20_prev"]*0.95: position+=5
    if latest["close"]>=latest["high50_prev"]*0.90: position+=5
    if latest["distance_ma20"]<=0.15: position+=5
    rs_score=0
    if rs20>0: rs_score+=5
    if rs60>0: rs_score+=5
    if rs120>0: rs_score+=5
    score=max(0,min(100,round(trend+momentum+volume+position+rs_score,1)))
    rating="D" if avoid or breakdown else "A+" if score>=85 and not overextended else "A" if score>=75 else "B+" if score>=65 else "B" if score>=55 else "C" if score>=45 else "D"
    if latest["close"]<latest["ma50"] and latest["rsi14"]<45: rating="D"
    if overextended and rating=="A+": rating="A"
    # state
    if latest["close"]>latest["ma20"]>latest["ma50"]>latest["ma100"] and latest["rsi14"]>60 and latest["macd"]>latest["macd_signal"] and latest["macd"]>0 and latest["close"]>=latest["high20_prev"]*0.95:
        trend_state="STRONG_UPTREND"
    elif latest["close"]>latest["ma20"] and latest["close"]>latest["ma50"] and latest["ma20"]>latest["ma50"] and latest["rsi14"]>50:
        trend_state="UPTREND"
    elif accumulation:
        trend_state="SIDEWAY_ACCUMULATION"
    elif breakdown:
        trend_state="BREAKDOWN"
    elif latest["close"]<latest["ma20"] and latest["close"]<latest["ma50"] and latest["ma20"]<latest["ma50"]:
        trend_state="DOWNTREND"
    else:
        trend_state="SIDEWAY"
    action="AVOID" if rating=="D" else "WAIT PULLBACK" if overextended else "WATCH BREAKOUT" if accumulation or reclaim else "WATCH" if rating in ["A+","A","B+"] else "WAIT"
    lv=levels(df,c)
    alerts=[]
    if breakout: alerts.append(f"[BREAKOUT] {symbol} vượt high 20 phiên, volume {safe_float(latest['vol_ratio'])}x, RSI {safe_float(latest['rsi14'])}, score {score}.")
    if reclaim: alerts.append(f"[RECLAIM] {symbol} lấy lại MA20/MA50, RSI {safe_float(latest['rsi14'])}, MACD cải thiện.")
    if breakdown: alerts.append(f"[BREAKDOWN] {symbol} thủng nền/low 20 phiên, RSI {safe_float(latest['rsi14'])}, volume {safe_float(latest['vol_ratio'])}x.")
    if overextended: alerts.append(f"[OVEREXTENDED] {symbol} cách MA20 {safe_float(latest['distance_ma20']*100)}%, RSI {safe_float(latest['rsi14'])}, tránh mua đuổi.")
    if pullback: alerts.append(f"[PULLBACK] {symbol} điều chỉnh về MA20, RSI giữ trên 50.")
    if rs20>0.05: alerts.append(f"[RS] {symbol} khỏe hơn thị trường 20 phiên khoảng {safe_float(rs20*100)}%.")
    warnings=[]
    if false_breakout: warnings.append("Có dấu hiệu breakout giả: râu trên dài, volume lớn nhưng đóng dưới kháng cự.")
    if overextended: warnings.append("Mã khỏe nhưng đã xa MA20, ưu tiên chờ pullback hoặc tạo nền.")
    if avoid: warnings.append("Doanh nghiệp có thể tốt nhưng chart kỹ thuật đang yếu, không ưu tiên điểm mua.")
    comment=f"{symbol}: {trend_state}, rating {rating}, score {score}. "
    if breakout: comment+="Breakout có xác nhận volume. "
    elif reclaim: comment+="Đang reclaim MA20/MA50, cần vượt kháng cự gần để khỏe hơn. "
    elif accumulation: comment+="Đang tích lũy, chờ breakout khỏi nền. "
    elif breakdown or avoid: comment+="Chart yếu/thủng nền, loại khỏi nhóm mua kỹ thuật. "
    elif overextended: comment+="Xu hướng mạnh nhưng quá xa MA20, tránh mua đuổi. "
    return {"ticker":symbol,"name":NAMES.get(symbol,symbol),"sector":SECTORS.get(symbol,"Khác"),"close":safe_float(c,0),"%change":safe_float((c/float(prev['close'])-1)*100,2),"score":score,"rating":rating,"trend_state":trend_state,"actionTag":action,"signals":{"above_ma20":bool(latest["close"]>latest["ma20"]),"above_ma50":bool(latest["close"]>latest["ma50"]),"above_ma100":bool(latest["close"]>latest["ma100"]),"above_ma200":bool(latest["close"]>latest["ma200"]),"rsi14":safe_float(latest["rsi14"]),"macd_positive":bool(latest["macd"]>0),"volume_ratio":safe_float(latest["vol_ratio"]),"relative_strength_20d":safe_float(rs20,3),"relative_strength_60d":safe_float(rs60,3),"breakout":breakout,"false_breakout":false_breakout,"breakdown":breakdown,"overextended":overextended,"accumulation":accumulation,"reclaim":reclaim,"pullback":pullback,"avoid":avoid,"lower_wick":lower_wick_long and close_near_high,"upper_wick":upper_wick_long},"levels":lv,"subscores":{"trend":trend,"momentum":momentum,"volume":volume,"position":position,"relativeStrength":rs_score},"alerts":alerts,"comment":comment,"warnings":warnings}

def main():
    errors={}
    bench_ret20=bench_ret60=bench_ret120=None
    for b in ["VNINDEX","VN30","VN30INDEX"]:
        try:
            bdf,_=fetch_history(b)
            bdf=add_indicators(bdf)
            c=float(bdf.iloc[-1]["close"])
            bench_ret20=c/float(bdf.iloc[-21]["close"])-1 if len(bdf)>21 else 0
            bench_ret60=c/float(bdf.iloc[-61]["close"])-1 if len(bdf)>61 else 0
            bench_ret120=c/float(bdf.iloc[-121]["close"])-1 if len(bdf)>121 else 0
            break
        except Exception as e:
            errors[b]=str(e)
    results=[]
    for s in WATCHLIST:
        try:
            df,src=fetch_history(s)
            item=classify_and_score(s,df,bench_ret20,bench_ret60,bench_ret120)
            results.append(item)
            print("OK",s,item["rating"],item["score"],item["trend_state"])
        except Exception as e:
            errors[s]=str(e)
            print("ERR",s,e)
    if results:
        results=sorted(results,key=lambda x:x.get("score",0),reverse=True)
        data={"meta":{"updated_at":datetime.now(VN_TZ).strftime("%Y-%m-%d %H:%M:%S VN"),"source":"Vnstock Technical Market Scanner","universe":len(WATCHLIST),"success":len(results),"note":"MA, RSI, MACD, Volume, breakout/breakdown, RS, support/resistance, rating A+ to D.","errors":errors},"stocks":results}
    else:
        data={"meta":{"updated_at":datetime.now(VN_TZ).strftime("%Y-%m-%d %H:%M:%S VN"),"source":"fallback empty","universe":len(WATCHLIST),"note":"Không lấy được dữ liệu.","errors":errors},"stocks":[]}
    Path("data.json").write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding="utf-8")
    print("Wrote data.json",len(results))

if __name__=="__main__":
    main()
