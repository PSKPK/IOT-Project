<?php

    $host = "localhost";		// host = localhost because database hosted on the same server where PHP files are hosted
    $dbname = "iot";		// Database name
    $username = "root";	// Database username
    $password = "";	// Database password

// Establish connection to MySQL database
$conn = new mysqli($host, $username, $password, $dbname);

// Check if connection established successfully
if ($conn->connect_error) {
    die("Connection failed: " . $conn->connect_error);
}

else { echo "Connected to mysql database. "; }

// If values send by NodeMCU are not empty then insert into MySQL database table
  if(!empty($_POST['sendval']) && !empty($_POST['sendval2']) )
    {   
		$val = $_POST['sendval'];
        $val2 = $_POST['sendval2'];

// Update your tablename here
            $res = $conn->query('SELECT * FROM `SENSOR_DATA` WHERE D_DATE=CURRENT_DATE AND TIME_TO_SEC(TIMEDIFF(CURRENT_TIME, T_TIME))<5');
            if (mysqli_num_rows($res)==0)
	        {$sql = "INSERT INTO `SENSOR_DATA` (`D_DATE`,`T_TIME`,`T_TEMP`,`M_MOVE`) VALUES (CURRENT_DATE, CURRENT_TIME, ".$val.", ".$val2.")";

		if ($conn->query($sql) === TRUE) {
		    echo "Values inserted in MySQL database table.";
		} else {
		    echo "Error: " . $sql . "<br>" . $conn->error;
		}}
	}


// Close MySQL connection
$conn->close();



?>
