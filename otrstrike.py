import streamlit as st
import pandas as pd
import smtplib
import base64
from io import BytesIO
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import LinearSegmentedColormap

# Title and Introduction
st.title("OTR Baseball Metrics Analyzer")
st.write("Upload your Bat Speed and Exit Velocity CSV files to generate a comprehensive report.")

# File Uploads
bat_speed_file = st.file_uploader("Upload Bat Speed File", type="csv")
exit_velocity_file = st.file_uploader("Upload Exit Velocity File", type="csv")

# Dropdown for Bat Speed Level
bat_speed_level = st.selectbox(
    "Select Player Level for Bat Speed",
    ["Youth", "High School", "College", "Indy", "Affiliate"]
)

# Dropdown for Exit Velocity Level
exit_velocity_level = st.selectbox(
    "Select Player Level for Exit Velocity",
    ["10u", "12u", "14u", "JV/16u", "Var/18u", "College", "Indy", "Affiliate"]
)

# Debugging: Ensure levels are selected correctly
st.write(f"Selected Bat Speed Level: {bat_speed_level}")
st.write(f"Selected Exit Velocity Level: {exit_velocity_level}")

benchmarks = {
    "10u": {
        "Avg EV": 50, "Top 8th EV": 61,
        "Avg LA": 12.14, "HHB LA": 8.78
    },
    "12u": {
        "Avg EV": 59, "Top 8th EV": 72,
        "Avg LA": 12.14, "HHB LA": 8.78
    },
    "14u": {
        "Avg EV": 68, "Top 8th EV": 80,
        "Avg LA": 12.14, "HHB LA": 8.78
    },
    "JV/16u": {
        "Avg EV": 72.65, "Top 8th EV": 85,
        "Avg LA": 16.51, "HHB LA": 11.47
    },
    "Var/18u": {
        "Avg EV": 78.0, "Top 8th EV": 91.5,
        "Avg LA": 16.51, "HHB LA": 11.47
    },
    "Youth": {
        "Avg EV": 58.4, "Top 8th EV": 70.19, "Avg LA": 12.14, "HHB LA": 8.78,
        "Avg BatSpeed": 49.21, "90th% BatSpeed": 52.81, "Avg TimeToContact": 0.19, "Avg AttackAngle": 11.78
    },
    "High School": {
        "Avg EV": 74.54, "Top 8th EV": 86.75, "Avg LA": 16.51, "HHB LA": 11.47,
        "Avg BatSpeed": 62.4, "90th% BatSpeed": 67.02, "Avg TimeToContact": 0.163, "Avg AttackAngle": 9.8
    },
    "College": {
        "Avg EV": 81.57, "Top 8th EV": 94.44, "Avg LA": 17.57, "HHB LA": 12.86,
        "Avg BatSpeed": 67.53, "90th% BatSpeed": 72.54, "Avg TimeToContact": 0.154, "Avg AttackAngle": 10.52
    },
    "Indy": {
        "Avg EV": 85.99, "Top 8th EV": 98.12, "Avg LA": 18.68, "HHB LA": 14.74,
        "Avg BatSpeed": 69.2, "90th% BatSpeed": 74.04, "Avg TimeToContact": 0.154, "Avg AttackAngle": 10.62
    },
    "Affiliate": {
        "Avg EV": 85.49, "Top 8th EV": 98.71, "Avg LA": 18.77, "HHB LA": 15.55,
        "Avg BatSpeed": 70.17, "90th% BatSpeed": 75.14, "Avg TimeToContact": 0.147, "Avg AttackAngle": 11.09
    }
}

def evaluate_performance(metric, benchmark, lower_is_better=False, special_metric=False):
    if special_metric:
        if benchmark - 3 <= metric <= benchmark:
            return "Average"
        elif metric < benchmark - 3:
            return "Below Average"
        else:
            return "Above Average"
    else:
        if lower_is_better:
            if metric < benchmark:
                return "Above Average"
            elif metric <= benchmark * 1.1:
                return "Average"
            else:
                return "Below Average"
        else:
            if metric > benchmark:
                return "Above Average"
            elif metric >= benchmark * 0.9:
                return "Average"
            else:
                return "Below Average"

# Process Bat Speed File (Skip the first 8 rows)
bat_speed_metrics = None
if bat_speed_file:
    df_bat_speed = pd.read_csv(bat_speed_file, skiprows=8)
    bat_speed_data = pd.to_numeric(df_bat_speed.iloc[:, 7], errors='coerce')  # Column H: Bat Speed
    attack_angle_data = pd.to_numeric(df_bat_speed.iloc[:, 10], errors='coerce')  # Column K: Attack Angle
    time_to_contact_data = pd.to_numeric(df_bat_speed.iloc[:, 15], errors='coerce')  # Time to Contact

    player_avg_bat_speed = bat_speed_data.mean()
    top_10_percent_bat_speed = bat_speed_data.quantile(0.90)
    avg_attack_angle_top_10 = attack_angle_data[bat_speed_data >= top_10_percent_bat_speed].mean()
    avg_time_to_contact = time_to_contact_data.mean()

    bat_speed_benchmark = benchmarks[bat_speed_level]["Avg BatSpeed"]
    top_90_benchmark = benchmarks[bat_speed_level]["90th% BatSpeed"]
    time_to_contact_benchmark = benchmarks[bat_speed_level]["Avg TimeToContact"]
    attack_angle_benchmark = benchmarks[bat_speed_level]["Avg AttackAngle"]

    bat_speed_metrics = (
        "### Bat Speed Metrics\n"
        f"- **Player Average Bat Speed:** {player_avg_bat_speed:.2f} mph (Benchmark: {bat_speed_benchmark} mph)\n"
        f"  - Player Grade: {evaluate_performance(player_avg_bat_speed, bat_speed_benchmark)}\n"
        f"- **Top 10% Bat Speed:** {top_10_percent_bat_speed:.2f} mph (Benchmark: {top_90_benchmark} mph)\n"
        f"  - Player Grade: {evaluate_performance(top_10_percent_bat_speed, top_90_benchmark)}\n"
        f"- **Average Attack Angle (Top 10% Bat Speed Swings):** {avg_attack_angle_top_10:.2f}° (Benchmark: {attack_angle_benchmark}°)\n"
        f"  - Player Grade: {evaluate_performance(avg_attack_angle_top_10, attack_angle_benchmark)}\n"
        f"- **Average Time to Contact:** {avg_time_to_contact:.3f} sec (Benchmark: {time_to_contact_benchmark} sec)\n"
        f"  - Player Grade: {evaluate_performance(avg_time_to_contact, time_to_contact_benchmark, lower_is_better=True)}\n"
    )

# Process Exit Velocity File (No rows skipped)
exit_velocity_metrics = None
strike_zone_img_html = ""  # We'll embed an image of the strike zone
if exit_velocity_file:
    df_exit_velocity = pd.read_csv(exit_velocity_file)
    try:
        if len(df_exit_velocity.columns) > 9:
            strike_zone_data = df_exit_velocity.iloc[:, 5]   # Column F: Strike Zone
            exit_velocity_data = pd.to_numeric(df_exit_velocity.iloc[:, 7], errors='coerce')  # H: Velo
            launch_angle_data = pd.to_numeric(df_exit_velocity.iloc[:, 8], errors='coerce')   # I: LA
            distance_data = pd.to_numeric(df_exit_velocity.iloc[:, 9], errors='coerce')       # J: Dist

            non_zero_ev_rows = exit_velocity_data[exit_velocity_data > 0]

            if not non_zero_ev_rows.empty:
                # Calculate Exit Velocity Metrics
                exit_velocity_avg = non_zero_ev_rows.mean()
                top_8_percent_exit_velocity = non_zero_ev_rows.quantile(0.92)

                top_8_mask = exit_velocity_data >= top_8_percent_exit_velocity
                avg_launch_angle_top_8 = launch_angle_data[top_8_mask].mean()
                avg_distance_top_8 = distance_data[top_8_mask].mean()
                total_avg_launch_angle = launch_angle_data[launch_angle_data > 0].mean()

                ev_benchmark = benchmarks[exit_velocity_level]["Avg EV"]
                top_8_benchmark = benchmarks[exit_velocity_level]["Top 8th EV"]
                la_benchmark = benchmarks[exit_velocity_level]["Avg LA"]
                hhb_la_benchmark = benchmarks[exit_velocity_level]["HHB LA"]

                exit_velocity_metrics = (
                    "### Exit Velocity Metrics\n"
                    f"- **Average Exit Velocity:** {exit_velocity_avg:.2f} mph (Benchmark: {ev_benchmark} mph)\n"
                    f"  - Player Grade: {evaluate_performance(exit_velocity_avg, ev_benchmark, special_metric=True)}\n"
                    f"- **Top 8% Exit Velocity:** {top_8_percent_exit_velocity:.2f} mph (Benchmark: {top_8_benchmark} mph)\n"
                    f"  - Player Grade: {evaluate_performance(top_8_percent_exit_velocity, top_8_benchmark, special_metric=True)}\n"
                    f"- **Average Launch Angle (On Top 8% Exit Velocity Swings):** {avg_launch_angle_top_8:.2f}° (Benchmark: {hhb_la_benchmark}°)\n"
                    f"  - Player Grade: {evaluate_performance(avg_launch_angle_top_8, hhb_la_benchmark)}\n"
                    f"- **Total Average Launch Angle (Avg LA):** {total_avg_launch_angle:.2f}° (Benchmark: {la_benchmark}°)\n"
                    f"  - Player Grade: {evaluate_performance(total_avg_launch_angle, la_benchmark)}\n"
                    f"- **Average Distance (8% swings):** {avg_distance_top_8:.2f} ft\n"
                )

                # Compute frequency of top 8% EV in each zone
                top_8_df = df_exit_velocity[top_8_mask].copy()
                top_8_df["StrikeZone"] = top_8_df.iloc[:, 5]
                zone_counts = top_8_df["StrikeZone"].value_counts()

                # Zones of interest layout
                zone_layout = [
                    [10, None, 11],
                    [1,   2,    3],
                    [4,   5,    6],
                    [7,   8,    9],
                    [12, None, 13]
                ]

                # Get max count for normalization
                max_count = zone_counts.max() if not zone_counts.empty else 0

                # Create a custom colormap from dark blue -> grey -> red
                cmap = LinearSegmentedColormap.from_list('strikezones', ['darkblue', 'grey', 'red'])

                fig, ax = plt.subplots(figsize=(3,5))
                ax.axis('off')

                cell_width = 1.0
                cell_height = 1.0

                # Plot each cell
                for r, row_zones in enumerate(zone_layout):
                    for c, z in enumerate(row_zones):
                        x = c * cell_width
                        # invert y to start top row at top
                        y = (len(zone_layout)-1 - r) * cell_height
                        if z is not None:
                            count = zone_counts.get(z, 0)
                            norm_val = (count / max_count) if max_count > 0 else 0
                            color = cmap(norm_val)
                            rect = plt.Rectangle((x, y), cell_width, cell_height, facecolor=color, edgecolor='black')
                            ax.add_patch(rect)
                            # Add text (zone number)
                            ax.text(x+0.5*cell_width, y+0.5*cell_height, str(z), ha='center', va='center', fontsize=10, color='black')
                        else:
                            # Just a blank cell
                            rect = plt.Rectangle((x, y), cell_width, cell_height, facecolor='white', edgecolor='black')
                            ax.add_patch(rect)

                ax.set_xlim(0, 3*cell_width)
                ax.set_ylim(0, 5*cell_height)

                # Convert figure to base64
                buf = BytesIO()
                plt.savefig(buf, format='png', bbox_inches='tight')
                buf.seek(0)
                img_data = base64.b64encode(buf.read()).decode('utf-8')
                plt.close(fig)

                strike_zone_img_html = f"<h3>Strike Zone Top 8% Exit Velocities</h3><img src='data:image/png;base64,{img_data}'/>"

            else:
                st.error("No valid Exit Velocity data found in the file. Please check the data.")
        else:
            st.error("The uploaded file does not have the required columns for Exit Velocity.")
    except Exception as e:
        st.error(f"An error occurred while processing the Exit Velocity file: {e}")

# Display Results
st.write("## Calculated Metrics")
if bat_speed_metrics:
    st.markdown(bat_speed_metrics)
if exit_velocity_metrics:
    st.markdown(exit_velocity_metrics)
    if strike_zone_img_html:
        st.markdown(strike_zone_img_html, unsafe_allow_html=True)

player_name = st.text_input("Enter Player Name")
date_range = st.text_input("Enter Date Range")

# Email Configuration
email_address = "otrdatatrack@gmail.com"  # Your email address
email_password = "pslp fuab dmub cggo"  # Your app-specific password
smtp_server = "smtp.gmail.com"
smtp_port = 587

def send_email_report(recipient_email, bat_speed_metrics, exit_velocity_metrics, player_name, date_range, bat_speed_level, exit_velocity_level, strike_zone_img_html):
    msg = MIMEMultipart()
    msg['From'] = email_address
    msg['To'] = recipient_email
    msg['Subject'] = "OTR Baseball Metrics and Grade Report"

    email_body = f"""
    <html>
    <body style="color: black; background-color: white;">
        <h2 style="color: black;">OTR Metrics Report</h2>
        <p style="color: black;"><strong>Player Name:</strong> {player_name}</p>
        <p style="color: black;"><strong>Date Range:</strong> {date_range}</p>
    """

    if bat_speed_metrics:
        email_body += f"<p style='color: black;'><strong>Bat Speed Level:</strong> {bat_speed_level}</p>"
    if exit_velocity_metrics:
        email_body += f"<p style='color: black;'><strong>Exit Velocity Level:</strong> {exit_velocity_level}</p>"

    email_body += "<p style='color: black;'>The following data is constructed with benchmarks for each level.</p>"

    if bat_speed_metrics:
        email_body += f"""
        <h3 style="color: black;">Bat Speed Metrics</h3>
        <p><strong>Player Average Bat Speed:</strong> {player_avg_bat_speed:.2f} mph (Benchmark: {bat_speed_benchmark} mph)
        <br>Player Grade: {evaluate_performance(player_avg_bat_speed, bat_speed_benchmark)}</p>

        <p><strong>Top 10% Bat Speed:</strong> {top_10_percent_bat_speed:.2f} mph (Benchmark: {top_90_benchmark} mph)
        <br>Player Grade: {evaluate_performance(top_10_percent_bat_speed, top_90_benchmark)}</p>

        <p><strong>Average Attack Angle (Top 10% Bat Speed Swings):</strong> {avg_attack_angle_top_10:.2f}° (Benchmark: {attack_angle_benchmark}°)
        <br>Player Grade: {evaluate_performance(avg_attack_angle_top_10, attack_angle_benchmark)}</p>

        <p><strong>Average Time to Contact:</strong> {avg_time_to_contact:.3f} sec (Benchmark: {time_to_contact_benchmark} sec)
        <br>Player Grade: {evaluate_performance(avg_time_to_contact, time_to_contact_benchmark, lower_is_better=True)}</p>
        """

    if exit_velocity_metrics:
        email_body += f"""
        <h3 style="color: black;">Exit Velocity Metrics</h3>
        <p><strong>Average Exit Velocity:</strong> {exit_velocity_avg:.2f} mph (Benchmark: {ev_benchmark} mph)
        <br>Player Grade: {evaluate_performance(exit_velocity_avg, ev_benchmark, special_metric=True)}</p>

        <p><strong>Top 8% Exit Velocity:</strong> {top_8_percent_exit_velocity:.2f} mph (Benchmark: {top_8_benchmark} mph)
        <br>Player Grade: {evaluate_performance(top_8_percent_exit_velocity, top_8_benchmark, special_metric=True)}</p>

        <p><strong>Average Launch Angle (On Top 8% Exit Velocity Swings):</strong> {avg_launch_angle_top_8:.2f}° (Benchmark: {hhb_la_benchmark}°)
        <br>Player Grade: {evaluate_performance(avg_launch_angle_top_8, hhb_la_benchmark)}</p>

        <p><strong>Total Average Launch Angle (Avg LA):</strong> {total_avg_launch_angle:.2f}° (Benchmark: {la_benchmark}°)
        <br>Player Grade: {evaluate_performance(total_avg_launch_angle, la_benchmark)}</p>

        <p><strong>Average Distance (8% swings):</strong> {avg_distance_top_8:.2f} ft</p>
        {strike_zone_img_html}
        """

    email_body += "<p style='color: black;'>Best Regards,<br>OTR Baseball</p></body></html>"

    msg.attach(MIMEText(email_body, 'html'))

    try:
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(email_address, email_password)
            server.send_message(msg)
        st.success("Report sent successfully!")
    except Exception as e:
        st.error(f"Failed to send email: {e}")

st.write("## Email the Report")
recipient_email = st.text_input("Enter Email Address")

if st.button("Send Report"):
    if recipient_email:
        send_email_report(
            recipient_email,
            bat_speed_metrics,
            exit_velocity_metrics,
            player_name,
            date_range,
            bat_speed_level,
            exit_velocity_level,
            strike_zone_img_html
        )
    else:
        st.error("Please enter a valid email address.")

