rm -rf build/
mkdir -p build/temp/
pip install . --target build/temp/
cd build/temp && zip -r ../Lambda.zip .
rm -rf build/temp/