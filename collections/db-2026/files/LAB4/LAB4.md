# LAB4

## 1

```mysql
CREATE DATABASE course_select_sys;
-- 创建学生表
CREATE TABLE S (
    SID VARCHAR(10) PRIMARY KEY,
    SNAME VARCHAR(50) NOT NULL,
    AGE INT,
    SEX CHAR(1)
);

-- 创建课程表
CREATE TABLE C (
    CID VARCHAR(10) PRIMARY KEY,
    CNAME VARCHAR(100) NOT NULL,
    TEACHER VARCHAR(50) NOT NULL
);

-- 创建选课表
CREATE TABLE SC (
    SID VARCHAR(10),
    CID VARCHAR(10),
    GRADE INT,
    PRIMARY KEY (SID, CID),
    FOREIGN KEY (SID) REFERENCES S(SID),
    FOREIGN KEY (CID) REFERENCES C(CID)
);

-- 插入学生数据
INSERT INTO S (SID, SNAME, AGE, SEX) VALUES
('S1', 'Wang feng', 20, 'M'),
('S2', 'Liu fang', 19, 'M'),
('S3', 'Chen yun', 22, 'M'),
('S4', 'Wu kai', 19, 'M'),
('S5', 'Liu li', 21, 'F'),
('S6', 'Dong qing', 18, 'F');

-- 插入课程数据
INSERT INTO C (CID, CNAME, TEACHER) VALUES
('C1', 'DB', 'Li'),
('C2', 'maths', 'Ma'),
('C3', 'chemistry', 'Zhou'),
('C4', 'physics', 'Shi'),
('C5', 'OS', 'Wen');

-- 插入选课数据
INSERT INTO SC (SID, CID, GRADE) VALUES
('S1', 'C1', 70),
('S2', 'C1', 81),
('S3', 'C1', 92),
('S4', 'C1', 85),
('S1', 'C2', 65),
('S2', 'C3', 57),
('S3', 'C5', 87);
```

![image-20260430232444436](C:\Users\***\AppData\Roaming\Typora\typora-user-images\image-20260430232444436.png)

## 2

### a

```mysql
-- 创建函数：统计某个学生选修的课程数量
DELIMITER $$

CREATE FUNCTION GetStudentCourseCount(p_SID VARCHAR(10))
RETURNS INT
DETERMINISTIC
READS SQL DATA
BEGIN
    DECLARE course_count INT;
    SELECT COUNT(*) INTO course_count
    FROM SC
    WHERE SID = p_SID;

    RETURN course_count;
END$$

DELIMITER ;
```

![image-20260430233114373](C:\Users\***\AppData\Roaming\Typora\typora-user-images\image-20260430233114373.png)

### b

```mysql
-- 添加学分列
ALTER TABLE C ADD COLUMN CREDITS INT DEFAULT 3;

-- 设置每门课程的学分（可自定义）
UPDATE C SET CREDITS = 3 WHERE CID IN ('C2', 'C3');
UPDATE C SET CREDITS = 2 WHERE CID IN ('C1', 'C4');
UPDATE C SET CREDITS = 4 WHERE CID IN ('C5');

DELIMITER $$

CREATE PROCEDURE GetStudentTotalCreditsWithCredits(IN student_id VARCHAR(10))
BEGIN
    DECLARE total_credits INT DEFAULT 0;

    -- 计算总学分（根据课程表实际学分）
    SELECT SUM(c.CREDITS) INTO total_credits
    FROM SC sc
    JOIN C c ON sc.CID = c.CID
    WHERE sc.SID = student_id;

    -- 查询学生信息和总学分
    SELECT
        s.SID,
        s.SNAME,
        s.AGE,
        s.SEX,
        IFNULL(total_credits, 0) AS total_credits,
        COUNT(sc.CID) AS course_count,
        GROUP_CONCAT(CONCAT(c.CNAME, '(', c.CREDITS, '学分)') SEPARATOR ', ') AS course_list
    FROM S s
    LEFT JOIN SC sc ON s.SID = sc.SID
    LEFT JOIN C c ON sc.CID = c.CID
    WHERE s.SID = student_id
    GROUP BY s.SID, s.SNAME, s.AGE, s.SEX;
END$$

DELIMITER ;
```

![image-20260430233554912](C:\Users\***\AppData\Roaming\Typora\typora-user-images\image-20260430233554912.png)

## 3

```mysql
-- a) 删除学生信息时，自动删除SC表中该学生的选课记录
DELIMITER $$

CREATE TRIGGER delete_student_cascade
BEFORE DELETE ON S
FOR EACH ROW
BEGIN
    -- 删除该学生的所有选课记录
    DELETE FROM SC WHERE SID = OLD.SID;
END$$

DELIMITER ;


-- b) 添加选课信息时，确保课程存在
DELIMITER $$

CREATE TRIGGER check_course_exists
BEFORE INSERT ON SC
FOR EACH ROW
BEGIN
    DECLARE course_exists INT;

    -- 检查课程是否存在
    SELECT COUNT(*) INTO course_exists
    FROM C
    WHERE CID = NEW.CID;

    -- 如果课程不存在，则阻止插入并报错
    IF course_exists = 0 THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = '错误：课程不存在，无法添加选课记录！';
    END IF;
END$$

DELIMITER ;
```

## 4

```java
package com.example;

import java.sql.*;
import java.util.Scanner;

public class CourseSelectionSystem {

    // 数据库连接参数
    private static final String URL = "jdbc:mysql://localhost:3306/course_select_sys?useSSL=false&serverTimezone=UTC";
    private static final String USERNAME = "root";
    private static final String PASSWORD = "********"; // 请修改为你的数据库密码

    private Connection connection;
    private Scanner scanner;
    private String currentStudentId;

    public CourseSelectionSystem() {
        scanner = new Scanner(System.in);
    }

    // a) 数据库连接
    public void connectToDatabase() throws SQLException {
        try {
            // 加载MySQL驱动（MySQL 8.0以上版本可省略，但保留以兼容旧版本）
            Class.forName("com.mysql.cj.jdbc.Driver");

            // 建立连接
            connection = DriverManager.getConnection(URL, USERNAME, PASSWORD);
            System.out.println("数据库连接成功！");
        } catch (ClassNotFoundException e) {
            System.out.println("MySQL驱动未找到: " + e.getMessage());
            throw new SQLException("驱动加载失败");
        } catch (SQLException e) {
            System.out.println("数据库连接失败: " + e.getMessage());
            throw e;
        }
    }

    // 学生登录
    public boolean login() {
        System.out.print("请输入学号: ");
        currentStudentId = scanner.nextLine().trim();

        String sql = "SELECT * FROM S WHERE SID = ?";
        try (PreparedStatement pstmt = connection.prepareStatement(sql)) {
            pstmt.setString(1, currentStudentId);
            ResultSet rs = pstmt.executeQuery();

            if (rs.next()) {
                System.out.println("欢迎 " + rs.getString("SNAME") + " 同学！");
                return true;
            } else {
                System.out.println("学号不存在，请重新输入！");
                return false;
            }
        } catch (SQLException e) {
            System.out.println("登录失败: " + e.getMessage());
            return false;
        }
    }

    // b) 读取可选课程信息（学生未选的课程）
    public void viewAvailableCourses() {
        System.out.println("\n========== 可选课程列表 ==========");

        String sql = "SELECT C.CID, C.CNAME, C.TEACHER " +
                "FROM C " +
                "WHERE C.CID NOT IN (SELECT CID FROM SC WHERE SID = ?)";

        try (PreparedStatement pstmt = connection.prepareStatement(sql)) {
            pstmt.setString(1, currentStudentId);
            ResultSet rs = pstmt.executeQuery();

            System.out.printf("%-10s %-20s %-15s\n", "课程号", "课程名", "任课教师");
            System.out.println("----------------------------------------");

            boolean hasCourses = false;
            while (rs.next()) {
                hasCourses = true;
                System.out.printf("%-10s %-20s %-15s\n",
                        rs.getString("CID"),
                        rs.getString("CNAME"),
                        rs.getString("TEACHER"));
            }

            if (!hasCourses) {
                System.out.println("暂无可选课程（可能已选修所有课程）");
            }
        } catch (SQLException e) {
            System.out.println("查询可选课程失败: " + e.getMessage());
        }
    }

    // c) 选课
    public void selectCourse() {
        viewAvailableCourses();

        System.out.print("\n请输入要选修的课程号: ");
        String courseId = scanner.nextLine().trim();

        // 检查课程是否存在
        String checkCourseSql = "SELECT * FROM C WHERE CID = ?";
        String checkSelectionSql = "SELECT * FROM SC WHERE SID = ? AND CID = ?";
        String insertSql = "INSERT INTO SC (SID, CID, GRADE) VALUES (?, ?, NULL)";

        try {
            // 检查课程是否存在
            PreparedStatement checkCourseStmt = connection.prepareStatement(checkCourseSql);
            checkCourseStmt.setString(1, courseId);
            ResultSet courseRs = checkCourseStmt.executeQuery();

            if (!courseRs.next()) {
                System.out.println("错误：课程不存在！");
                return;
            }

            // 检查是否已选过该课程
            PreparedStatement checkSelectionStmt = connection.prepareStatement(checkSelectionSql);
            checkSelectionStmt.setString(1, currentStudentId);
            checkSelectionStmt.setString(2, courseId);
            ResultSet selectionRs = checkSelectionStmt.executeQuery();

            if (selectionRs.next()) {
                System.out.println("错误：你已经选修过该课程！");
                return;
            }

            // 执行选课
            PreparedStatement insertStmt = connection.prepareStatement(insertSql);
            insertStmt.setString(1, currentStudentId);
            insertStmt.setString(2, courseId);
            int rows = insertStmt.executeUpdate();

            if (rows > 0) {
                System.out.println("选课成功！");
            }

        } catch (SQLException e) {
            System.out.println("选课失败: " + e.getMessage());
        }
    }

    // d) 读取选修课程信息（查看已选课程）
    public void viewSelectedCourses() {
        System.out.println("\n========== 已选课程列表 ==========");

        String sql = "SELECT SC.CID, C.CNAME, C.TEACHER, SC.GRADE " +
                "FROM SC " +
                "JOIN C ON SC.CID = C.CID " +
                "WHERE SC.SID = ? " +
                "ORDER BY SC.CID";

        try (PreparedStatement pstmt = connection.prepareStatement(sql)) {
            pstmt.setString(1, currentStudentId);
            ResultSet rs = pstmt.executeQuery();

            System.out.printf("%-10s %-20s %-15s %-10s\n", "课程号", "课程名", "任课教师", "成绩");
            System.out.println("--------------------------------------------------");

            boolean hasCourses = false;
            while (rs.next()) {
                hasCourses = true;
                String grade = rs.getString("GRADE");
                String gradeDisplay = (grade == null) ? "未录入" : grade;
                System.out.printf("%-10s %-20s %-15s %-10s\n",
                        rs.getString("CID"),
                        rs.getString("CNAME"),
                        rs.getString("TEACHER"),
                        gradeDisplay);
            }

            if (!hasCourses) {
                System.out.println("尚未选修任何课程");
            }

            // 显示总学分和选课数量
            getStudentSummary();

        } catch (SQLException e) {
            System.out.println("查询已选课程失败: " + e.getMessage());
        }
    }

    // 获取学生选课汇总信息
    private void getStudentSummary() {
        String sql = "SELECT COUNT(*) as course_count, COUNT(*) * 3 as total_credits " +
                "FROM SC WHERE SID = ?";

        try (PreparedStatement pstmt = connection.prepareStatement(sql)) {
            pstmt.setString(1, currentStudentId);
            ResultSet rs = pstmt.executeQuery();

            if (rs.next()) {
                int courseCount = rs.getInt("course_count");
                int totalCredits = rs.getInt("total_credits");
                System.out.println("\n选课统计：");
                System.out.println("选修课程数: " + courseCount);
                System.out.println("总学分: " + totalCredits + " 学分");
            }
        } catch (SQLException e) {
            System.out.println("查询汇总信息失败: " + e.getMessage());
        }
    }

    // e) 退选课程
    public void dropCourse() {
        viewSelectedCourses();

        System.out.print("\n请输入要退选的课程号: ");
        String courseId = scanner.nextLine().trim();

        String sql = "DELETE FROM SC WHERE SID = ? AND CID = ?";

        try (PreparedStatement pstmt = connection.prepareStatement(sql)) {
            pstmt.setString(1, currentStudentId);
            pstmt.setString(2, courseId);
            int rows = pstmt.executeUpdate();

            if (rows > 0) {
                System.out.println("退选成功！");
                // 显示更新后的选课列表
                viewSelectedCourses();
            } else {
                System.out.println("退选失败：未找到该选课记录");
            }
        } catch (SQLException e) {
            System.out.println("退选失败: " + e.getMessage());
        }
    }

    // 查看课程选修情况（管理员视角）
    public void viewCourseEnrollment() {
        System.out.println("\n========== 课程选修情况统计 ==========");

        String sql = "SELECT C.CID, C.CNAME, C.TEACHER, " +
                "COUNT(SC.SID) as student_count, " +
                "ROUND(AVG(SC.GRADE), 2) as avg_grade " +
                "FROM C " +
                "LEFT JOIN SC ON C.CID = SC.CID " +
                "GROUP BY C.CID, C.CNAME, C.TEACHER " +
                "ORDER BY student_count DESC";

        try (Statement stmt = connection.createStatement();
             ResultSet rs = stmt.executeQuery(sql)) {

            System.out.printf("%-10s %-20s %-15s %-12s %-10s\n",
                    "课程号", "课程名", "任课教师", "选修人数", "平均成绩");
            System.out.println("------------------------------------------------------------");

            while (rs.next()) {
                String avgGrade = rs.getString("avg_grade");
                String avgDisplay = (avgGrade == null) ? "0" : avgGrade;
                System.out.printf("%-10s %-20s %-15s %-12s %-10s\n",
                        rs.getString("CID"),
                        rs.getString("CNAME"),
                        rs.getString("TEACHER"),
                        rs.getInt("student_count"),
                        avgDisplay);
            }

        } catch (SQLException e) {
            System.out.println("查询课程统计失败: " + e.getMessage());
        }
    }

    // 显示主菜单
    public void showMenu() {
        System.out.println("\n========== 选课系统菜单 ==========");
        System.out.println("1. 查看可选课程");
        System.out.println("2. 选修课程");
        System.out.println("3. 查看已选课程");
        System.out.println("4. 退选课程");
        System.out.println("5. 查看所有课程选修情况（统计）");
        System.out.println("6. 切换学生");
        System.out.println("0. 退出系统");
        System.out.print("请选择操作: ");
    }

    // 运行主程序
    public void run() {
        try {
            connectToDatabase();

            // 首次登录
            while (currentStudentId == null) {
                login();
            }

            int choice;
            do {
                showMenu();
                choice = scanner.nextInt();
                scanner.nextLine(); // 清除缓冲区

                switch (choice) {
                    case 1:
                        viewAvailableCourses();
                        break;
                    case 2:
                        selectCourse();
                        break;
                    case 3:
                        viewSelectedCourses();
                        break;
                    case 4:
                        dropCourse();
                        break;
                    case 5:
                        viewCourseEnrollment();
                        break;
                    case 6:
                        currentStudentId = null;
                        while (currentStudentId == null) {
                            login();
                        }
                        break;
                    case 0:
                        System.out.println("感谢使用选课系统，再见！");
                        break;
                    default:
                        System.out.println("无效选择，请重新输入！");
                }
            } while (choice != 0);

        } catch (SQLException e) {
            System.out.println("系统初始化失败: " + e.getMessage());
        } finally {
            // 关闭资源
            try {
                if (connection != null && !connection.isClosed()) {
                    connection.close();
                    System.out.println("数据库连接已关闭");
                }
                if (scanner != null) {
                    scanner.close();
                }
            } catch (SQLException e) {
                System.out.println("关闭连接失败: " + e.getMessage());
            }
        }
    }

    // 主方法
    public static void main(String[] args) {
        CourseSelectionSystem system = new CourseSelectionSystem();
        system.run();
    }
}
```

### b

![image-20260501000352943](C:\Users\***\AppData\Roaming\Typora\typora-user-images\image-20260501000352943.png)

### c

![image-20260501000410916](C:\Users\***\AppData\Roaming\Typora\typora-user-images\image-20260501000410916.png)

### d

![image-20260501000427507](C:\Users\***\AppData\Roaming\Typora\typora-user-images\image-20260501000427507.png)

### e

![image-20260501000451259](C:\Users\***\AppData\Roaming\Typora\typora-user-images\image-20260501000451259.png)

### f

![image-20260501000509881](C:\Users\***\AppData\Roaming\Typora\typora-user-images\image-20260501000509881.png)

## 5

### a

```shell
mysqldump -u root -p course_select_sys > D:\Documentary\Table\SHIT\数据库系统\backup\course_db_backup.sql
mysql -u root -p course_select_sys < D:\Documentary\Table\SHIT\数据库系统\backup\course_db_backup.sql
```

### b

![image-20260501000958372](C:\Users\***\AppData\Roaming\Typora\typora-user-images\image-20260501000958372.png)

![image-20260501001144464](C:\Users\***\AppData\Roaming\Typora\typora-user-images\image-20260501001144464.png)