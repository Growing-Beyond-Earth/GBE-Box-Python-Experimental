import re

def columns(stat):
    return(str(stat["yea"]) + "-"
        + str("%02d" % stat["mon"]) + "-"
        + str("%02d" % stat["day"]) + " "
        + str("%02d" % stat["hou"]) + ":"
        + str("%02d" % stat["min"]) + ":"
        + str("%02d" % stat["sec"]) + "  "
        + str("%3.f" % stat["red"]) + " "
        + str("%3.f" % stat["gre"]) + " "
        + str("%3.f" % stat["blu"]) + " "
        + str("%3.f" % stat["whi"]) + "  "
        + str("%5.2f" % stat["vol"]) + " "
        + str("%4.f" % stat["mam"]) + " "
        + str("%5.2f" % stat["wat"]) + "  "
        + str("%3.f" % stat["fan"]) + " " 
        + str("%4.f" % stat["rpm"]) + "  "
        + str("%5.2f" % stat["sst"]) + " "
        + str("%4.f" % stat["ssm"]))

def ymd(stat):
    return(str(stat["yea"]) + "-"
        + str("%02d" % stat["mon"]) + "-"
        + str("%02d" % stat["day"]))

def hourlog_head():
    return("\"Date\",\"Time\",\"Red\",\"Green\",\"Blue\",\"White\",\"Volts\",\"Milliamps\",\"Watts\",\"Fan\",\"Fan RPM\",\"Temperature\",\"Soil moisture\"\n")

def hourlog(stat, log_avg):
    return(str(stat["yea"]) + "-"
        + str("%02d" % stat["mon"]) + "-"
        + str("%02d" % stat["day"]) + "\t"
        + str("%02d" % stat["hou"]) + ":"
        + str("%02d" % stat["min"]) + "\t"
        + str(round(log_avg["red"])) + "\t"
        + str(round(log_avg["gre"])) + "\t"
        + str(round(log_avg["blu"])) + "\t"
        + str(round(log_avg["whi"])) + "\t"
        + str(round(log_avg["vol"], 2)) + "\t"
        + str(round(log_avg["mam"])) + "\t"
        + str(round(log_avg["wat"], 2)) + "\t"
        + str(round(log_avg["fan"])) + "\t" 
        + str(round(log_avg["rpm"])) + "\t"
        + str(log_avg["sst"]) + "\t"
        + str(round(log_avg["ssm"])))

def url_query(stat, log_avg):
    return("boa=" + str(stat["boa"]) + "&"
        +  "dat=" + str(stat["yea"]) + "-" + str("%02d" % stat["mon"]) + "-" + str("%02d" % stat["day"]) + "&"
        +  "tim=" + str("%02d" % stat["hou"]) + ":" +  str("%02d" % stat["min"]) + "&"
        +  "red=" + str(round(log_avg["red"])) + "&"
        +  "gre=" + str(round(log_avg["gre"])) + "&"
        +  "blu=" + str(round(log_avg["blu"])) + "&"
        +  "whi=" + str(round(log_avg["whi"])) + "&"
        +  "vol=" + str(round(log_avg["vol"], 2)) + "&"
        +  "mam=" + str(round(log_avg["mam"])) + "&"
        +  "wat=" + str(round(log_avg["wat"], 2)) + "&"
        +  "fan=" + str(round(log_avg["fan"])) + "&"
        +  "rpm=" + str(round(log_avg["rpm"])) + "&"
        +  "sst=" + str(round(log_avg["sst"], 2)) + "&"
        +  "ssm=" + str(round(log_avg["ssm"])) + "&"
        +  "con=" + str(stat["con"]) + "&"
        +  "cof=" + str(stat["cof"]) + "&"
        +  "cf0=" + str(stat["cf0"]) + "&"
        +  "cf1=" + str(stat["cf1"]) + "&"
        +  "cre=" + str(stat["cre"]) + "&"
        +  "cgr=" + str(stat["cgr"]) + "&"
        +  "cbl=" + str(stat["cbl"]) + "&"
        +  "cwh=" + str(stat["cwh"]) + "&"
        +  "ctz=" + str(stat["ctz"])
       )


def valid_config(config):
# time
    regex = "^([01]?[0-9]|2[0-3]):[0-5][0-9]$";
    p = re.compile(regex)
    try:
        if re.search(p, config['lights']['timer']['on']) is None: return False
    except: return False
    try:
        if re.search(p, config['lights']['timer']['off']) is None: return False
    except: return False

# lights and fan
    try:
        if isinstance(config['lights']['duty']['red'], int) and config['lights']['duty']['red'] >= 0 and config['lights']['duty']['red'] <= 200: pass
        else: return False
    except: return False
    try:
        if isinstance(config['lights']['duty']['green'], int) and config['lights']['duty']['green'] >= 0 and config['lights']['duty']['green'] <= 89: pass
        else: return False
    except: return False
    try:
        if isinstance(config['lights']['duty']['blue'], int) and config['lights']['duty']['blue'] >= 0 and config['lights']['duty']['blue'] <= 94: pass
        else: return False
    except: return False
    try:
        if isinstance(config['lights']['duty']['white'], int) and config['lights']['duty']['white'] >= 0 and config['lights']['duty']['white'] <= 146: pass
        else: return False
    except: return False
    try:
        if isinstance(config['fan']['duty']['when lights on'], int) and config['fan']['duty']['when lights on'] >= 0 and config['fan']['duty']['when lights on'] <= 255: pass
        else: return False
    except: return False
    try:
        if isinstance(config['fan']['duty']['when lights off'], int) and config['fan']['duty']['when lights off'] >= 0 and config['fan']['duty']['when lights off'] <= 255: pass
        else: return False
    except: return False
    try:
        if config['time zone']['GMT offset'] >= -11 and config['time zone']['GMT offset'] <= 13: pass
        else: return False
    except: return False


    return True

