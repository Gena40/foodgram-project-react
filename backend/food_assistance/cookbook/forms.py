from django import forms


class RecipeIngredientsFormset(forms.models.BaseInlineFormSet):
    def clean(self) -> None:
        count_ingr = 0
        count_del = 0
        for form in self.forms:
            if form.cleaned_data:
                count_ingr += 1
                if form.cleaned_data.get('DELETE'):
                    count_del += 1
        if count_ingr < 1 or count_ingr == count_del:
            raise forms.ValidationError(
                'Рецепт должен содержать хотя бы 1 ингредиент.'
            )
