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

else { echo "Connected to mysql database. <br>"; }

// Select values from MySQL database table
$sql = "SELECT `D_DATE`,`T_TIME`,`T_TEMP`,`M_MOVE` FROM `SENSOR_DATA` WHERE T_TIME > CURRENT_TIME-180";  // Update your tablename here

$result = $conn->query($sql);

echo "<center>";

$count = 0;
if ($result->num_rows > 0) {

    // output data of each row
    $count = $count + 1;
    while($row = $result->fetch_assoc()) {
        echo "<strong> Id:</strong> " . $count . " &nbsp <strong>Date :</strong> " . $row["D_DATE"]. " &nbsp <strong>TIME :</strong> " . $row["T_TIME"]. " &nbsp <strong>TEMP :</strong> " . $row["T_TEMP"]." &nbsp <strong>MOVE :</strong>" .$row["M_MOVE"]. "<p>";

}
} else {
    echo "0 results";
}

echo "</center>";

$conn->close();

?>
