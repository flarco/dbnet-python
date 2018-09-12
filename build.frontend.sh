DIR=$(cd "$(dirname "$0")"; pwd)
cd $DIR/frontend
npm run build
mv dist ../dbnet
cd ../dbnet
rm -rf templates
rm -rf static
mv dist templates
mv templates/static .
mkdir -p static/css/static
mv static/fonts static/css/static