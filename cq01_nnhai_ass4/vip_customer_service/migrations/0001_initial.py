# Generated by Django 3.2.18 on 2025-04-09 09:27

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='VipBenefit',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('description', models.TextField()),
                ('benefit_type', models.CharField(choices=[('discount', 'Discount'), ('free_shipping', 'Free Shipping'), ('gift', 'Free Gift'), ('early_access', 'Early Access'), ('cashback', 'Cashback'), ('exclusive', 'Exclusive Product')], max_length=20)),
                ('applicable_level', models.CharField(choices=[('silver', 'Silver'), ('gold', 'Gold'), ('platinum', 'Platinum'), ('diamond', 'Diamond')], max_length=20)),
                ('discount_value', models.DecimalField(blank=True, decimal_places=2, max_digits=5, null=True)),
                ('is_active', models.BooleanField(default=True)),
            ],
            options={
                'ordering': ['applicable_level', 'name'],
            },
        ),
        migrations.CreateModel(
            name='VipMembership',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('customer_id', models.IntegerField(unique=True)),
                ('level', models.CharField(choices=[('silver', 'Silver'), ('gold', 'Gold'), ('platinum', 'Platinum'), ('diamond', 'Diamond')], default='silver', max_length=20)),
                ('points', models.IntegerField(default=0)),
                ('joined_at', models.DateTimeField(auto_now_add=True)),
                ('expires_at', models.DateTimeField()),
                ('is_active', models.BooleanField(default=True)),
            ],
            options={
                'ordering': ['-level', '-points'],
            },
        ),
        migrations.CreateModel(
            name='VipTransaction',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('transaction_type', models.CharField(choices=[('earn', 'Points Earned'), ('redeem', 'Points Redeemed'), ('expire', 'Points Expired'), ('adjust', 'Points Adjusted')], max_length=20)),
                ('points', models.IntegerField()),
                ('description', models.CharField(max_length=255)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('reference_id', models.CharField(blank=True, max_length=100, null=True)),
                ('membership', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='transactions', to='vip_customer_service.vipmembership')),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
    ]
