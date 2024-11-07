#include <linux/kernel.h>
#include <linux/init.h>
#include <linux/module.h>

#include <linux/proc_fs.h>
#include <linux/slab.h>

#include <asm/io.h>

#define LLL_MAX_USER_SIZE 1024

#define BCM2837_GPIO_ADDRESS 0x3F200000
#define BCM2711_GPIO_ADDRESS 0xfe200000

static struct proc_dir_entry *lll_proc = NULL;

static char data_buffer[LLL_MAX_USER_SIZE+1] = {0};

static unsigned int *gpio_registers = NULL;

static void gpio_pin_on(unsigned int pin)
{
	unsigned int fsel_index = pin/10;
	unsigned int fsel_bitpos = pin%10;
	unsigned int* gpio_fsel = gpio_registers + fsel_index;
	unsigned int* gpio_on_register = (unsigned int*)((char*)gpio_registers + 0x1c);

	*gpio_fsel &= ~(7 << (fsel_bitpos*3));
	*gpio_fsel |= (1 << (fsel_bitpos*3));
	*gpio_on_register |= (1 << pin);

	return;
}

static void gpio_pin_off(unsigned int pin)
{
	unsigned int *gpio_off_register = (unsigned int*)((char*)gpio_registers + 0x28);
	*gpio_off_register |= (1<<pin);
	return;
}

ssize_t lll_read(struct file *file, char __user *user, size_t size, loff_t *off)
{
	return copy_to_user(user,"Hello!\n", 7) ? 0 : 7;
}

ssize_t lll_write(struct file *file, const char __user *user, size_t size, loff_t *off)
{
	unsigned int pin = UINT_MAX;
	unsigned int value = UINT_MAX;

	memset(data_buffer, 0x0, sizeof(data_buffer));

	if (size > LLL_MAX_USER_SIZE)
	{
		size = LLL_MAX_USER_SIZE;
	}

	if (copy_from_user(data_buffer, user, size))
		return 0;

	printk("Data buffer: %s\n", data_buffer);

	if (sscanf(data_buffer, "%d,%d", &pin, &value) != 2)
	{
		printk("Inproper data format submitted\n");
		return size;
	}

	if (pin > 21 || pin < 0)
	{
		printk("Invalid pin number submitted\n");
		return size;
	}

	if (value != 0 && value != 1)
	{
		printk("Invalid on/off value\n");
		return size;
	}

	printk("You said pin %d, value %d\n", pin, value);
	if (value == 1)
	{
		gpio_pin_on(pin);
	} else if (value == 0)
	{
		gpio_pin_off(pin);
	}

	return size;
}

static const struct proc_ops lll_proc_fops =  // proc_ops scheint ein codewort zu sein. Kernelversion abhängig!
	// was die struktur macht, ist, wenn der user den file ließt(cat proc-fs ll-gpio wird lll_read ausgeführt
{
	.proc_read = lll_read, // wenn der Benutzer den file ließt also: cat proc-fs lll-gpio wird func lll_read ausgeführt
	.proc_write = lll_write,  // und wenn geschrieben wird wir func lll_write laufen.
};


static int __init gpio_driver_init(void)  // startfunktion !!!
{
	printk("Welcome to my driver!\n");

	gpio_registers = (int*)ioremap(BCM2711_GPIO_ADDRESS, PAGE_SIZE);

	if (gpio_registers == NULL)
	{
		printk("Failed to map GPIO memory to driver\n");
		return -1;
	}

	printk("Successfully mapped in GPIO memory\n");

	// create an entry in the proc-fs
	lll_proc = proc_create("lll-gpio", 0666, NULL, &lll_proc_fops); // instructions for kernel mod driver to create the "lll-gpio" file to the proc-fs system (proc interface name, Zugangsberechtigung!!! 0666, NULL=some flags, setzt parameter zur adresse=lll_proc_flops
	if (lll_proc == NULL)
	{
		return -1;
	}

	return 0;
}

static void __exit gpio_driver_exit(void)
{
	printk("Leaving my driver!\n");
	iounmap(gpio_registers);
	proc_remove(lll_proc);
	return;
}

module_init(gpio_driver_init); // bei installation des Modules(insmod) wird die func als erstes ausgeführt.
module_exit(gpio_driver_exit); // die func wird aufgerufen wenn ich das module wieder entferne (rmmod)

MODULE_LICENSE("GPL");
MODULE_AUTHOR("Low Level Learning");
MODULE_DESCRIPTION("Test of writing drivers for RASPI");
MODULE_VERSION("1.0");




// insmod =install module

// erklärung von Variable: static const struct proc_ops lll_proc_fops =
	// static: The static keyword limits the visibility of lll_proc_fops to the current source file. This means that the lll_proc_fops structure cannot be accessed or linked from other source files, which helps in encapsulating functionality within the file.
	// const: The const keyword indicates that lll_proc_fops is a constant, meaning its values cannot be changed after initialization. This ensures that the structure and its contents are immutable once defined.
	// struct proc_ops: This declares a variable of type struct proc_ops, which is a structure that likely holds function pointers or operations related to processes in the Linux kernel. The proc_ops structure is typically used for defining file operations for entries in the /proc filesystem.
	// lll_proc_fops: This is the name of the variable being declared. It represents an instance of the proc_ops structure, which will likely define a set of operations (such as read, write, open, etc.) for a file or directory in the /proc filesystem.

