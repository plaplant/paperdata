rm -r paperdev_dbi/
cp -r paperdata_dbi/ paperdev_dbi/
mv paperdev_dbi/scripts/paperdata_db.py paperdev_dbi/scripts/paperdev_db.py
sed -i 's/paperdata/paperdev/g' paperdev_dbi/*.py
sed -i 's/paperdata/paperdev/g' paperdev_dbi/scripts/*.py
