import os
import pandas as pd

import pymysql # mysql.connector
from sqlalchemy import create_engine


def save_db(host, user, password, port):
    directory_path = './data'
    all_files = os.listdir(directory_path)
    csv_files = [file for file in all_files if file.endswith('.csv')]

    for csv_file in csv_files:
        file_path = os.path.join(directory_path, csv_file)
        df = pd.read_csv(file_path)
        df = df.fillna('')

        table_name = os.path.splitext(csv_file)[0]

        # SQL 연결
        try:
            connection = pymysql.connect(
                host=host,
                user=user,
                password=password,
                port=port,
            )
            cursor = connection.cursor()
            print('Success connection.')
        except pymysql.MySQLError as connect_err:
            print("Error connection.", connect_err)

        # DATABASE 생성
        try:
            cursor.execute("CREATE DATABASE IF NOT EXISTS job_database;")
            cursor.execute("USE job_database;")
            print('Success create database.')
        except pymysql.MySQLError as connect_err:
            print("Error create database.", connect_err)

        cursor.close()
        connection.close()

        # SQL 다시 연결
        try:
            connection = pymysql.connect(
                host=host,
                user=user,
                password=password,
                database='job_database',
                port=port,
            )
            cursor = connection.cursor()
            print('Success connection.')
        except pymysql.MySQLError as connect_err:
            print("Error connection.", connect_err)

        # TABLE 생성
        try:
            create_table = f"""
                CREATE TABLE {table_name} (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    link TEXT NOT NULL,
                    title TEXT NOT NULL,
                    company TEXT NOT NULL,
                    mainwork TEXT NOT NULL,
                    requirement TEXT NOT NULL,
                    preferential TEXT NOT NULL,
                    skill TEXT NOT NULL,
                    due TEXT NOT NULL,
                    workplace TEXT NOT NULL,
                    intro TEXT NOT NULL,
                    benefit TEXT NOT NULL,
                    label TEXT NOT NULL
                );
            """
            cursor.execute(create_table)
            print('Success create table.')
        except pymysql.MySQLError as table_err:
            print("Error create table.", table_err)

        connection.commit()

        # 데이터가 있는지 확인
        select_count = f"SELECT COUNT(*) FROM {table_name}"
        cursor.execute(select_count)
        result = cursor.fetchone()
        record_count = result[0]

        # 기존 데이터 삭제
        if record_count > 0:
            try:
                delete_sql = f"DELETE FROM {table_name}"
                cursor.execute(delete_sql)
                print("Success delete data.")
            except pymysql.MySQLError as delete_err:
                print("Error delete data.", delete_err)
        else:
            print("No delete data.")

        # AUTO_INCREMENT 초기화
        try:
            auto_increment = f"ALTER TABLE {table_name} AUTO_INCREMENT = 1"
            cursor.execute(auto_increment)
            connection.commit()
            print("Success AUTO_INCREMENT value reset.")
        except pymysql.MySQLError as auto_increment_err:
            print("Error AUTO_INCREMENT value reset.", auto_increment_err)

        for i in range(len(df)):
            sql = f"""
            INSERT INTO {table_name}
            (link, title, company, mainwork, requirement, preferential, skill, due, workplace, intro, benefit, label) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            val = (
                df.iloc[i]['link'],
                df.iloc[i]['title'],
                df.iloc[i]['company'],
                df.iloc[i]['mainwork'],
                df.iloc[i]['requirement'],
                df.iloc[i]['preferential'],
                df.iloc[i]['skill'],
                df.iloc[i]['due'],
                df.iloc[i]['workplace'],
                df.iloc[i]['intro'],
                df.iloc[i]['benefit'],
                df.iloc[i]['label'],
            )
            cursor.execute(sql, val)
        connection.commit()

        if connection.open:
            cursor.close()
            connection.close()
            print("MySQL connection is closed")