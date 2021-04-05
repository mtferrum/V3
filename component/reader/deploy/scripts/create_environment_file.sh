#Create openvino_python.env file with PYTHONPATH and LD_LIBRARY_PATH variables in a given path (defaults to /etc/spyspace/
OUTPUT_PATH=$(realpath ${1:-"/etc/spyspace"})/openvino_python.env;
(
    source /opt/intel/openvino/bin/setupvars.sh;
    printf "PYTHONPATH=${PYTHONPATH}\nLD_LIBRARY_PATH=${LD_LIBRARY_PATH}" > "$OUTPUT_PATH";
)
if [ -f "$OUTPUT_PATH" ]; then
    echo "File ${OUTPUT_PATH} successfully created!";
    exit 0
fi
echo "ERROR: Failed to create file ${OUTPUT_PATH}";
exit $?
