<?php
    // Local XAMPP defaults remain unchanged; CI can provide DB_* variables.
    $hostEnv = getenv('DB_HOST');
    $userEnv = getenv('DB_USER');
    $passEnv = getenv('DB_PASSWORD');
    $dbEnv   = getenv('DB_NAME');
    $host     = ($hostEnv !== false && $hostEnv !== '') ? $hostEnv : 'localhost';
    $user     = ($userEnv !== false && $userEnv !== '') ? $userEnv : 'root';
    $password = ($passEnv !== false) ? $passEnv : '';
    $db       = ($dbEnv !== false && $dbEnv !== '') ? $dbEnv : 'quiz_pengupil';

    $con = mysqli_connect($host, $user, $password, $db);
    if (!$con) { 
        die("Connection failed: " . mysqli_connect_error());    
    }
?>
