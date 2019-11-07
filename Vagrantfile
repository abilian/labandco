# -*- mode: ruby -*-
# vi: set ft=ruby :

Vagrant.configure("2") do |config|
  config.vm.box = "debian/stretch64"
  config.vm.box_version = "9.8.0"
  config.vm.network "forwarded_port", guest: 443, host: 1443
  config.vm.network "forwarded_port", guest: 5000, host: 5000
  config.vm.provision :shell, inline: "/vagrant/etc/provision.sh"
end
