from django.db import models
from django.conf import settings


class Category(models.Model):
    CATEGORY_TYPES = [
        ('ingreso', 'Ingreso'),
        ('gasto', 'Gasto'),
    ]
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='categories',
        null=True, 
        blank=True
    )
    name = models.CharField(max_length=100, verbose_name='Nombre')
    category_type = models.CharField(max_length=10, choices=CATEGORY_TYPES, verbose_name='Tipo')
    color = models.CharField(max_length=7, default='#6366F1', verbose_name='Color')
    icon = models.CharField(max_length=50, default='tag', verbose_name='Icono')
    parent = models.ForeignKey(
        'self', 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True, 
        related_name='subcategories',
        verbose_name='Categoría padre'
    )
    is_default = models.BooleanField(default=False, verbose_name='Es predeterminada')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Categoría'
        verbose_name_plural = 'Categorías'
        ordering = ['category_type', 'name']
    
    def __str__(self):
        if self.parent:
            return f"{self.parent.name} > {self.name}"
        return self.name







