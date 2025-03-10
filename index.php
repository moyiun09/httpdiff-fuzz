<?php
// 这里要做到何种程度？
// 获取请求的内容，没问题吧，
$method = $_SERVER['REQUEST_METHOD'];
$url = $_SERVER['REQUEST_URI'];
$protocol = $_SERVER['SERVER_PROTOCOL'];
if ($_SERVER['QUERY_STRING'] == "") {
    $path = $_SERVER['PHP_SELF'];
} else {
    $path = $_SERVER['PHP_SELF'].'?'.$_SERVER['QUERY_STRING'];
}

$input = file_get_contents('php://input');
$headers = array();
// header 如何获取呢？
foreach ($_SERVER as $key => $value)
{
	//print($key."</br>");
	if(strpos($key,"HTTP") === 0){
		$headers[$key] = $value;
	}
		
}

$ret = array('method' => $method,'uri' => $path, 'protocol' => $protocol,'headers' => $headers, 'body'=>$input);
$ret = json_encode($ret);
$ret = str_replace("\\/", "/", $ret);
$ret = base64_encode($ret);
header('X-Req-Bytes: '.$ret);
echo 'This is a test message';
?>