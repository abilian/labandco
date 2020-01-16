# -*- mode: ruby -*-
# vi: set ft=ruby :

Vagrant.configure("2") do |config|
  config.vm.box = "debian/stretch64"
  config.vm.box_version = "9.9.1"
  config.vm.network "forwarded_port", guest: 443, host: 1443
  config.vm.network "forwarded_port", guest: 5000, host: 15000
  # config.vm.provision :shell, inline: "/vagrant/etc/provision.sh"
end
