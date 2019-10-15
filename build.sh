DIR=$(cd "$(dirname "$0")"; pwd)
cd $DIR/frontend
# cd frontend
npm install
npm run build
mv dist ../dbnet
cd ../dbnet
rm -f templates/index.html
rm -rf static
mv dist static
mv static/index.html templates
