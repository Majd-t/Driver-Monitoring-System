<?php
$conn = new mysqli("localhost", "root", "", "driver_monitoring");

if ($conn->connect_error) {
    die("Bağlantı hatası: " . $conn->connect_error);
}

// ضمان دعم الأحرف التركية
$conn->set_charset("utf8mb4");
?>

<!DOCTYPE html>
<html lang="tr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Sürücü İzleme Sistemi</title>
    <link href="https://fonts.googleapis.com/css2?family=Roboto:wght@400;700&display=swap" rel="stylesheet">
    <style>
        body {
            font-family: 'Roboto', sans-serif;
            background-color: #1E1E1E;
            color: #FFFFFF;
            margin: 0;
            padding: 20px;
            direction: ltr;
        }
        h1, h2, h3 {
            color: #4CAF50;
            text-align: center;
            margin-bottom: 20px;
            text-shadow: 0 2px 4px rgba(0, 0, 0, 0.5);
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
        }
        table {
            width: 100%;
            border-collapse: collapse;
            background-color: #2E2E2E;
            border-radius: 10px;
            overflow: hidden;
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.5);
            margin: 20px 0;
        }
        th, td {
            padding: 15px;
            text-align: left;
            border-bottom: 1px solid #555555;
        }
        th {
            background-color: #4CAF50;
            color: #FFFFFF;
            font-weight: bold;
            text-transform: uppercase;
        }
        tr {
            transition: background-color 0.3s ease;
        }
        tr:nth-child(even) {
            background-color: #333333;
        }
        tr:hover {
            background-color: #3A3A3A;
        }
        a {
            color: #2196F3;
            text-decoration: none;
            font-weight: bold;
            transition: color 0.3s ease;
        }
        a:hover {
            color: #4CAF50;
        }
        .back-button {
            display: inline-block;
            padding: 10px 20px;
            background-color: #2196F3;
            color: #FFFFFF;
            border-radius: 8px;
            margin-bottom: 20px;
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.5);
            transition: background-color 0.3s ease, transform 0.2s ease;
        }
        .back-button:hover {
            background-color: #1E87DB;
            transform: translateY(-2px);
        }
        .stats {
            background-color: #2E2E2E;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.5);
            margin-top: 20px;
        }
        .stats h3 {
            margin-top: 0;
            color: #4CAF50;
        }
        .stats p {
            margin: 10px 0;
            font-size: 16px;
            display: flex;
            justify-content: space-between;
            padding: 10px;
            background-color: #333333;
            border-radius: 5px;
            transition: background-color 0.3s ease;
        }
        .stats p:hover {
            background-color: #3A3A3A;
        }
        .stats p span {
            font-weight: bold;
            color: #4CAF50;
        }
        .no-data {
            text-align: center;
            color: #BBBBBB;
            font-style: italic;
        }
        @media (max-width: 768px) {
            table {
                font-size: 14px;
            }
            th, td {
                padding: 10px;
            }
            .back-button {
                padding: 8px 15px;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>Sürücü İzleme Sistemi</h1>

        <?php if (!isset($_GET['session_id'])) { ?>
            <h2>Kayıt Oturumları</h2>
            <table>
                <tr>
                    <th>Oturum Numarası</th>
                    <th>Başlangıç Zamanı</th>
                    <th>Detaylar</th>
                </tr>
                <?php
                $result = $conn->query("SELECT session_id, start_time FROM sessions ORDER BY start_time DESC");
                if ($result->num_rows > 0) {
                    while ($row = $result->fetch_assoc()) {
                        echo "<tr>
                                <td>" . $row['session_id'] . "</td>
                                <td>" . $row['start_time'] . "</td>
                                <td><a href='index.php?session_id=" . $row['session_id'] . "'>Detayları Görüntüle</a></td>
                              </tr>";
                    }
                } else {
                    echo "<tr><td colspan='3' class='no-data'>Hiç oturum bulunamadı.</td></tr>";
                }
                ?>
            </table>
        <?php } else {
            $session_id = intval($_GET['session_id']);
            ?>
            <h2>Oturum Numarası: <?php echo $session_id; ?> - Detaylar</h2>
            <a href="index.php" class="back-button">Oturum Listesine Geri Dön</a>

            <!-- جدول بيانات الجلسة -->
            <h3>Veri Kayıtları</h3>
            <table>
                <tr>
                    <th>Zaman Damgası</th>
                    <th>Durum</th>
                    <th>Göz Oranı (EAR)</th>
                    <th>Uyku Sayısı</th>
                    <th>Yorgunluk Sayısı</th>
                    <th>Aktif Sayısı</th>
                    <th>Uyku Süresi (s)</th>
                    <th>Yorgunluk Süresi (s)</th>
                    <th>Aktif Süre (s)</th>
                </tr>
                <?php
                $sql = "SELECT timestamp, status, ear, sleep_count, drowsy_count, active_count, sleep_duration, drowsy_duration, active_duration 
                        FROM driver_data 
                        WHERE session_id = ? 
                        ORDER BY timestamp";
                $stmt = $conn->prepare($sql);
                $stmt->bind_param("i", $session_id);
                $stmt->execute();
                $result = $stmt->get_result();

                if ($result->num_rows > 0) {
                    while ($row = $result->fetch_assoc()) {
                        echo "<tr>
                                <td>" . htmlspecialchars($row['timestamp']) . "</td>
                                <td>" . htmlspecialchars($row['status']) . "</td>
                                <td>" . htmlspecialchars($row['ear']) . "</td>
                                <td>" . htmlspecialchars($row['sleep_count']) . "</td>
                                <td>" . htmlspecialchars($row['drowsy_count']) . "</td>
                                <td>" . htmlspecialchars($row['active_count']) . "</td>
                                <td>" . htmlspecialchars($row['sleep_duration']) . "</td>
                                <td>" . htmlspecialchars($row['drowsy_duration']) . "</td>
                                <td>" . htmlspecialchars($row['active_duration']) . "</td>
                              </tr>";
                    }
                } else {
                    echo "<tr><td colspan='9' class='no-data'>Bu oturum için veri bulunamadı.</td></tr>";
                }
                $stmt->close();
                ?>
            </table>

            <!-- إحصائيات الجلسة -->
            <div class="stats">
                <h3>Oturum İstatistikleri</h3>
                <?php
                $sql = "SELECT 
                            MAX(sleep_count) as max_sleep, 
                            MAX(drowsy_count) as max_drowsy, 
                            MAX(active_count) as max_active, 
                            MAX(sleep_duration) as total_sleep_duration, 
                            MAX(drowsy_duration) as total_drowsy_duration, 
                            MAX(active_duration) as total_active_duration 
                        FROM driver_data 
                        WHERE session_id = ?";
                $stmt = $conn->prepare($sql);
                $stmt->bind_param("i", $session_id);
                $stmt->execute();
                $result = $stmt->get_result();
                $stats = $result->fetch_assoc();
                ?>
                <p>Uykuya Dalma Olayları: <span><?php echo $stats['max_sleep'] ?? 0; ?></span></p>
                <p>Yorgunluk Olayları: <span><?php echo $stats['max_drowsy'] ?? 0; ?></span></p>
                <p>Aktif Olaylar: <span><?php echo $stats['max_active'] ?? 0; ?></span></p>
                <p>Toplam Uyku Süresi (s): <span><?php echo $stats['total_sleep_duration'] ?? 0; ?></span></p>
                <p>Toplam Yorgunluk Süresi (s): <span><?php echo $stats['total_drowsy_duration'] ?? 0; ?></span></p>
                <p>Toplam Aktif Süre (s): <span><?php echo $stats['total_active_duration'] ?? 0; ?></span></p>
                <?php $stmt->close(); ?>
            </div>
        <?php } ?>

        <?php $conn->close(); ?>
    </div>
</body>
</html>