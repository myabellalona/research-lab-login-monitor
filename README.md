# Research Lab Login Monitor

A Python and Streamlit prototype that reviews simulated sign-ins to a fictional national security research laboratory's IT systems.

The project combines login-pattern detection, an interactive dashboard, a small threshold experiment, and research using public government advisories. The laboratory, accounts, systems, and IP addresses in the sample are fictional.

## What it does

- Loads login records from `sample_logs.csv`.
- Groups activity by account, source IP address, and target system.
- Flags groups with at least 3 or 5 failures within a five-minute window.
- Marks whether a successful login followed a qualifying failure burst within five minutes.
- Shows an alert table, a chart of total failures by account, and the underlying records.
- Calculates the experiment results using separately assigned labels for the supplied sample.
- Explains documented threat techniques and the prototype's coverage limits.

## Files

| File | Purpose |
| --- | --- |
| `app.py` | Detection logic, dashboard, experiment, and research section. |
| `sample_logs.csv` | The supplied 18 fictional login records. |
| `requirements.txt` | Python package versions for installation. |
| `.gitignore` | Excludes the local virtual environment and Python cache files from Git. |
| `README.md` | Setup, methods, results, references, and limitations. |

## Run on Windows

Use a terminal opened in the project folder. Python 3.13.14 was used for the guided setup.

Create the project's Python environment:

```powershell
python -m venv .venv
```

Install the dependencies:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

Start the dashboard:

```powershell
.\.venv\Scripts\python.exe -m streamlit run app.py
```

Open the Local URL printed in the terminal if the browser does not open automatically. If an optional email prompt appears, press Enter to skip it. Keep the terminal running while using the app; press Ctrl+C to stop it.

The dependency versions match the installed development environment: Streamlit 1.66.1 and pandas 3.1.0.

## Detection rules

**Rule 1: repeated failures.** At each failed-attempt time, count failures in the five-minute period ending at that time, including both endpoints. Flag a group if the count reaches the selected threshold. Failures do not have to be consecutive.

**Rule 2: success after a burst.** In that same account/IP/system group, check for a successful login strictly after a qualifying failed attempt and no more than five minutes later.

The alert table contains one summary row per flagged group across the file. It shows the largest failure count found in a five-minute window and whether any qualifying burst was followed by success.

The chart shows total failures per account across the entire file. This differs from the time-window count used by the detector.

## Supplied sample and experiment

The CSV has 18 records: 13 failures and 5 successes.

| Account | Assigned scenario |
| --- | --- |
| researcher1, engineer1, engineer2 | Ordinary successful logins. |
| analyst1 | Three ordinary password mistakes followed by success: benign. |
| admin1 | Six failures within two and a half minutes, followed by success: simulated suspicious activity. |
| researcher2 | Four failures within three minutes: simulated suspicious activity. |

These labels are evaluation inputs. The detector does not read them.

| Failure threshold | Suspicious cases detected | False alarms | Suspicious cases missed |
| --- | ---: | ---: | ---: |
| 3 | 2 | 1 | 0 |
| 5 | 1 | 0 | 1 |

At 3, the detector catches both suspicious cases but also flags analyst1's ordinary mistakes. At 5, it avoids that false alarm but misses researcher2.

This demonstrates a detection tradeoff on a tiny, constructed sample. These counts are not estimates of real-world detection accuracy. Review the assigned labels if the sample data changes.

## Research context

### Russia: GRU brute-force campaign, 2021

An NSA joint advisory described repeated password attempts against government and private-sector organizations.

**Project connection:** Some similar repeated attempts could trigger the prototype. Its grouping by one IP and one account can miss distributed activity.

[NSA: Brute Force Global Cyber Campaign, July 1, 2021](https://www.nsa.gov/Press-Room/Press-Releases-Statements/Press-Release-View/Article/2677750/nsa-partners-release-cybersecurity-advisory-on-brute-force-global-cyber-campaign/)

### Iran: credential attacks, 2024

A joint advisory described Iranian actors using brute force and compromised accounts against critical infrastructure organizations.

**Project connection:** A failure burst followed by success is worth investigating. Password spraying spread across many accounts may remain below this prototype's per-account threshold.

[Joint advisory AA24-290A, hosted by the Australian government](https://www.cyber.gov.au/advisory/iranian-cyber-actors-brute-force-and-credential-access-activity-compromises-critical-infrastructure)

### China: Volt Typhoon, 2024

A CISA joint advisory described Volt Typhoon activity involving valid accounts and legitimate system tools in critical infrastructure networks.

**Project connection:** A stolen password that succeeds immediately may trigger neither rule. This case illustrates the need for additional signals.

[CISA joint advisory AA24-038A, February 7, 2024](https://www.cisa.gov/sites/default/files/2024-03/aa24-038a_csa_prc_state_sponsored_actors_compromise_us_critical_infrastructure_3.pdf)

Government sources were checked on November 3, 2026. The project connections are inferences about the prototype's behavior. These sources do not attribute the fictional sample activity to any country, and they do not establish that all described campaigns targeted research laboratories.

## Limits and possible improvements

This is a learning prototype using a small local CSV. It does not connect to a real laboratory, block attacks, or establish attacker identity or nationality.

The rules can miss slow attempts, activity distributed across IPs or accounts, successful use of stolen credentials, and successes from a different IP or system. A flagged pattern can also be a legitimate user's mistakes.

Possible improvements include detecting attempts across accounts, tracking unfamiliar devices, and comparing activity with a user's usual behavior. These features are future work.

## Validation

The detection calculations were checked separately with the supplied sample, shuffled records, separated IPs and systems, empty data, and events exactly at or just outside the five-minute boundaries. Those checks ran under local pandas 2.2.3. The experiment calculations produced the table above.

To check the dashboard in the configured environment, move the threshold between 5 and 3. At 5, expect admin1 with a maximum of 6 failures and a checked success-after-burst box. At 3, also expect analyst1 and researcher2; researcher2's success-after-burst box should be unchecked.



