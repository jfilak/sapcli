from unittest.mock import Mock

GCTS_RESPONSE_FORBIDDEN = Mock(
    status_code=403,
    text='''<!DOCTYPE html>
<html><head>
<title>Application Server Error</title>
<style>
body { background: #ffffff; text-align: center; width:100%; height:100%; overflow:hidden; }
.content { display: table; position:absolute; width:100%; height:80%; }
.valigned { display: table-cell; vertical-align: middle; }
.lowerCenter { display: table-cell; vertical-align: bottom; }
.footer { position: absolute; bottom: 0; left: 0; width: 100%; z-index: -1; }
.footerLeft { float: left; margin-left: 20px; }
.footerRight { float: right; margin-right: 20px; position: absolute; bottom: 0px; right: 0px; }
.centerText { font-style: normal; font-family: Arial; font-size: 16px; color: #444444; z-index: 1; }
.errorTextHeader { font-style: normal; font-family: Arial; font-size: 40px; color: #444444; margin-top:0px; margin-bottom:12px; }
.detailText { font-style: normal; font-family: Arial; font-size: 16px; color: #444444; margin-top:0px; margin-bottom:0px; }
.bottomText { align: center; font-style: normal; font-family: Arial; font-size: 14px; color: #444444; }
.detailTable { align: bottom; vertical-align: middle; margin-left:auto; margin-right:auto; font-style: normal; font-family: Arial; font-size: 16px; color: #444444; }
</style></head>
<body>
<div class="content">
<div class="valigned">
<div class="centerText">
<p class="errorTextHeader"> <span >403 Forbidden</span> </p>

<p class="detailText"> <span id="msgText">The request has been blocked by UCON.</span></p>
<p class="detailText"> <span id="msgText">And the multiline
error message.</span></p>

<p class="detailText"> <span id="msgText">Server time:
<script>
var d = "20220725";
var t = "073947";
document.write(d.slice(0,4)+"-"+d.slice(4,6)+"-"+d.slice(6,8)+" "+t.slice(0,2)+":"+t.slice(2,4)+":"+t.slice(4,6)); </script>
</script>
</span> </p>
</div>
<table class="detailTable" border="0">
'''
)

GCTS_RESPONSE_FORBIDDEN_NO_ERROR_HEADER = Mock(
    status_code=403,
    text='''<!DOCTYPE html>
<html><head>
<title>Application Server Error</title>
<style>
body { background: #ffffff; text-align: center; width:100%; height:100%; overflow:hidden; }
.content { display: table; position:absolute; width:100%; height:80%; }
.valigned { display: table-cell; vertical-align: middle; }
.lowerCenter { display: table-cell; vertical-align: bottom; }
.footer { position: absolute; bottom: 0; left: 0; width: 100%; z-index: -1; }
.footerLeft { float: left; margin-left: 20px; }
.footerRight { float: right; margin-right: 20px; position: absolute; bottom: 0px; right: 0px; }
.centerText { font-style: normal; font-family: Arial; font-size: 16px; color: #444444; z-index: 1; }
.errorTextHeader { font-style: normal; font-family: Arial; font-size: 40px; color: #444444; margin-top:0px; margin-bottom:12px; }
.detailText { font-style: normal; font-family: Arial; font-size: 16px; color: #444444; margin-top:0px; margin-bottom:0px; }
.bottomText { align: center; font-style: normal; font-family: Arial; font-size: 14px; color: #444444; }
.detailTable { align: bottom; vertical-align: middle; margin-left:auto; margin-right:auto; font-style: normal; font-family: Arial; font-size: 16px; color: #444444; }
</style></head>
<body>
<div class="content">
<div class="valigned">
<div class="centerText">

<p class="detailText"> <span id="msgText">The request has been blocked by UCON.</span></p>
<p class="detailText"> <span id="msgText">And the multiline
error message.</span></p>

<p class="detailText"> <span id="msgText">Server time:
<script>
var d = "20220725";
var t = "073947";
document.write(d.slice(0,4)+"-"+d.slice(4,6)+"-"+d.slice(6,8)+" "+t.slice(0,2)+":"+t.slice(2,4)+":"+t.slice(4,6)); </script>
</script>
</span> </p>
</div>
<table class="detailTable" border="0">
'''
)

GCTS_RESPONSE_FORBIDDEN_NO_ERROR_MESSAGE = Mock(
    status_code=403,
    text='''<!DOCTYPE html>
<html><head>
<title>Application Server Error</title>
<style>
body { background: #ffffff; text-align: center; width:100%; height:100%; overflow:hidden; }
.content { display: table; position:absolute; width:100%; height:80%; }
.valigned { display: table-cell; vertical-align: middle; }
.lowerCenter { display: table-cell; vertical-align: bottom; }
.footer { position: absolute; bottom: 0; left: 0; width: 100%; z-index: -1; }
.footerLeft { float: left; margin-left: 20px; }
.footerRight { float: right; margin-right: 20px; position: absolute; bottom: 0px; right: 0px; }
.centerText { font-style: normal; font-family: Arial; font-size: 16px; color: #444444; z-index: 1; }
.errorTextHeader { font-style: normal; font-family: Arial; font-size: 40px; color: #444444; margin-top:0px; margin-bottom:12px; }
.detailText { font-style: normal; font-family: Arial; font-size: 16px; color: #444444; margin-top:0px; margin-bottom:0px; }
.bottomText { align: center; font-style: normal; font-family: Arial; font-size: 14px; color: #444444; }
.detailTable { align: bottom; vertical-align: middle; margin-left:auto; margin-right:auto; font-style: normal; font-family: Arial; font-size: 16px; color: #444444; }
</style></head>
<body>
<div class="content">
<div class="valigned">
<div class="centerText">
<p class="errorTextHeader"> <span >403 Forbidden</span> </p>
</div>
<table class="detailTable" border="0">
'''
)
