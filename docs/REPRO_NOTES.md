
## Chromatin Feature demo (Line B: extract_sigvar_demo)

Command:
cd "04_LOGO_Chromatin_Feature/2. result/0. demodata"
python extract_sigvar_demo.py demo_output.csv demo_sig.csv 3357 > extract_sigvar_demo.log 2>&1

Outputs:
- 04_LOGO_Chromatin_Feature/2. result/0. demodata/demo_sig.csv
- 04_LOGO_Chromatin_Feature/2. result/0. demodata/extract_sigvar_demo.log
- docs/lineB_sha256.txt


## Chromatin Feature demo (Line B: extract_sigvar_demo)

### Command
cd "04_LOGO_Chromatin_Feature/2. result/0. demodata"
python extract_sigvar_demo.py demo_output.csv demo_sig.csv 3357 > extract_sigvar_demo.log 2>&1

### Inputs
- 04_LOGO_Chromatin_Feature/2. result/0. demodata/demo_output.csv
- 04_LOGO_Chromatin_Feature/2. result/0. demodata/extract_sigvar_demo.py

### Outputs
- 04_LOGO_Chromatin_Feature/2. result/0. demodata/demo_sig.csv
- 04_LOGO_Chromatin_Feature/2. result/0. demodata/extract_sigvar_demo.log

### Evidence
- SHA256: docs/lineB_inputs_sha256.txt
- demo_sig.csv head: docs/lineB_demo_sig_head.txt
- env/pip freeze: docs/lineB_env.txt

