import streamlit as st
import pandas as pd


def find_alerts(logs, threshold):
    window = pd.Timedelta(minutes=5)
    alerts = []

    groups = logs.groupby(["username", "source_ip", "system"])
    for (username, source_ip, system), group in groups:
        failures = group.loc[group["result"] == "failure", "timestamp"]
        successes = group.loc[group["result"] == "success", "timestamp"]
        max_failures = 0
        success_after = False

        for time in failures:
            # Count failures in the five minutes ending at this attempt.
            count = int(failures.between(time - window, time).sum())
            max_failures = max(max_failures, count)

            if count >= threshold:
                # Check for a success within the next five minutes.
                following = successes[
                    (successes > time) & (successes <= time + window)
                ]
                if not following.empty:
                    success_after = True

        if max_failures >= threshold:
            alerts.append({
                "Account": username,
                "System": system,
                "Source IP": source_ip,
                "Most failures in 5 min": max_failures,
                "Success after burst": success_after,
            })

    return pd.DataFrame(alerts)


st.title("Research Lab Login Monitor")
st.write("A cybersecurity dashboard for a fictional national security research lab.")
st.write("This project uses simulated login records.")

logs = pd.read_csv("sample_logs.csv", parse_dates=["timestamp"])

threshold = st.select_slider(
    "Failed attempts needed within 5 minutes",
    options=[3, 5],
    value=5,
)

alerts = find_alerts(logs, threshold)

st.subheader("Suspicious login patterns")
st.write("Each row represents one account, source IP, and system.")
if alerts.empty:
    st.success("No sign-in patterns met this threshold.")
else:
    st.warning(f"{len(alerts)} sign-in pattern(s) need review.")
    st.dataframe(alerts, hide_index=True)
    st.write("A checked box means a success followed a qualifying burst within 5 minutes.")

st.subheader("Total failed attempts by account")
failed_counts = logs.loc[logs["result"] == "failure", "username"].value_counts()
st.bar_chart(failed_counts)

st.subheader("All login records")
st.dataframe(logs, hide_index=True)

st.subheader("Threshold experiment")
st.write(
    "In this sample, admin1 and researcher2 are simulated suspicious cases. "
    "The other accounts, including analyst1's password mistakes, are benign."
)

known_suspicious = {
    ("admin1", "198.51.100.25", "research-server"),
    ("researcher2", "203.0.113.50", "lab-vpn"),
}

experiment = []
for setting in [3, 5]:
    found = find_alerts(logs, setting)
    detected = set()

    for _, row in found.iterrows():
        detected.add((row["Account"], row["Source IP"], row["System"]))

    experiment.append({
        "Threshold": setting,
        "Suspicious cases detected": len(detected & known_suspicious),
        "False alarms": len(detected - known_suspicious),
        "Suspicious cases missed": len(known_suspicious - detected),
    })

st.dataframe(pd.DataFrame(experiment), hide_index=True)
st.caption("These results apply only to the supplied sample and its assigned labels.")

st.subheader("National security research")

st.markdown("""
**Russia — GRU brute-force campaign (2021):**
An NSA joint advisory described repeated password attempts against government
and private-sector organizations.
**Project connection:** Similar repeated attempts against one account could
trigger this monitor. Attempts spread across IP addresses could evade it.

[NSA source](https://www.nsa.gov/Press-Room/Press-Releases-Statements/Press-Release-View/Article/2677750/nsa-partners-release-cybersecurity-advisory-on-brute-force-global-cyber-campaign/)

**Iran — credential attacks (2024):**
A joint advisory described brute force and compromised accounts across
critical infrastructure sectors.
**Project connection:** Failure bursts followed by a successful login warrant
review. Password spraying across many accounts could evade this per-account rule.

[Joint advisory](https://www.cyber.gov.au/advisory/iranian-cyber-actors-brute-force-and-credential-access-activity-compromises-critical-infrastructure)

**China — Volt Typhoon (2024):**
A CISA joint advisory described access to critical infrastructure using valid
accounts and legitimate system tools.
**Project connection:** A stolen password that works immediately could trigger
neither rule. This shows why additional monitoring would be needed.

[CISA source](https://www.cisa.gov/sites/default/files/2024-03/aa24-038a_csa_prc_state_sponsored_actors_compromise_us_critical_infrastructure_3.pdf)
""")

st.info(
    "The research lab and login records are fictional. This prototype cannot "
    "identify an attacker's country or block attacks."
)