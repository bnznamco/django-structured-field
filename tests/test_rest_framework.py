import pytest
from rest_framework.test import APIClient

from tests.app.test_module.models import SimpleRelationModel, TestModel
from tests.utils.media import load_asset_and_remove_media


@pytest.mark.django_db
class TestRestFramework:
    def setup_method(self):
        self.client = APIClient()
        # Create some related objects for testing
        self.relation1 = SimpleRelationModel.objects.create(name="Relation 1")
        self.relation2 = SimpleRelationModel.objects.create(name="Relation 2")
        self.relation_with_file = SimpleRelationModel.objects.create(
            name="Relation with File",
            file=load_asset_and_remove_media("10595073.png")
        )
        
        # Create a test model with structured data
        self.test_model = TestModel.objects.create(
            title="Test Model",
            structured_data={
                "name": "Test Name",
                "age": 30,
                "child": {
                    "name": "Child Name",
                    "age": 5,
                    "fk_field": self.relation_with_file.pk,
                },
                "childs": [
                    {"name": "Child 1", "age": 10},
                    {"name": "Child 2", "age": 15}
                ],
                "fk_field": self.relation1.pk,
                "qs_field": [self.relation1.pk]
            }
        )
    
    def test_get_model(self):
        """Test retrieving a model with structured data"""
        response = self.client.get(f"/api/testmodels/{self.test_model.pk}/")
        assert response.status_code == 200
        
        data = response.json()
        assert data["title"] == "Test Model"
        assert data["structured_data"]["name"] == "Test Name"
        assert data["structured_data"]["age"] == 30
        assert data["structured_data"]["child"]["name"] == "Child Name"
        assert len(data["structured_data"]["childs"]) == 2
        assert data["structured_data"]["fk_field"]["id"] == self.relation1.pk
        assert self.relation1.pk in [el["id"] for el in data["structured_data"]["qs_field"]]
        assert data["structured_data"]["child"]["fk_field"]["id"] == self.relation_with_file.pk
        assert data["structured_data"]["child"]["fk_field"]["file"] is not None
        assert data["structured_data"]["child"]["fk_field"]["file"] == f"http://testserver/media/10595073.png"
        
    def test_create_model(self):
        """Test creating a model with structured data"""
        new_model_data = {
            "title": "New Model",
            "structured_data": {
                "name": "New Name",
                "age": 25,
                "child": {
                    "name": "New Child",
                    "age": 3
                },
                "childs": [
                    {"name": "New Child 1", "age": 8}
                ],
                "fk_field": self.relation2.pk,
                "qs_field": [self.relation1.pk, self.relation2.pk]
            },
            "structured_data_list": [
                {"name": "List Item 1", "age": 40, "qs_field": []}
            ]
        }
        
        response = self.client.post("/api/testmodels/", new_model_data, format="json")
        assert response.status_code == 201
        # Verify the model was created correctly
        created_id = response.json()["id"]
        created_model = TestModel.objects.get(pk=created_id)
        
        assert created_model.title == "New Model"
        assert created_model.structured_data.name == "New Name"
        assert created_model.structured_data.age == 25
        assert created_model.structured_data.fk_field.pk == self.relation2.pk
        assert len(created_model.structured_data.qs_field) == 2
        assert len(created_model.structured_data_list) == 1
    
    def test_update_model(self):
        """Test updating a model with structured data"""
        update_data = {
            "title": "Updated Model",
            "structured_data": {
                "name": "Updated Name",
                "age": 35,
                "child": {
                    "name": "Updated Child",
                    "age": 7
                },
                "childs": [
                    {"name": "Updated Child 1", "age": 12}
                ],
                "fk_field": self.relation2.pk,
                "qs_field": [self.relation2.pk]
            }
        }
        
        response = self.client.put(f"/api/testmodels/{self.test_model.pk}/", update_data, format="json")
        assert response.status_code == 200
        
        # Verify the model was updated correctly
        self.test_model.refresh_from_db()
        assert self.test_model.title == "Updated Model"
        assert self.test_model.structured_data.name == "Updated Name"
        assert self.test_model.structured_data.age == 35
        assert self.test_model.structured_data.fk_field.pk == self.relation2.pk
        assert len(self.test_model.structured_data.childs) == 1
        assert len(self.test_model.structured_data.qs_field) == 1
        assert self.test_model.structured_data.qs_field[0].pk == self.relation2.pk
    
    def test_patch_model(self):
        """Test partially updating a model with structured data"""
        patch_data = {
            "structured_data": {
                "name": "Patched Name",
                "child": {
                    "name": "Patched Child"
                },
                "qs_field": [self.relation1.pk]  # Required field
            }
        }
        
        response = self.client.patch(f"/api/testmodels/{self.test_model.pk}/", patch_data, format="json")
        assert response.status_code == 200
        
        # Verify only the specified fields were updated
        self.test_model.refresh_from_db()
        assert self.test_model.structured_data.name == "Patched Name"
        assert self.test_model.structured_data.age == 30  # Unchanged
        assert self.test_model.structured_data.child.name == "Patched Child"
        assert self.test_model.structured_data.child.age == 5  # Unchanged
        assert len(self.test_model.structured_data.childs) == 2  # Unchanged
        assert self.test_model.structured_data.fk_field.pk == self.relation1.pk  # Unchanged
    
    def test_patch_nested_list(self):
        """Test patching a nested list within structured data"""
        patch_data = {
            "structured_data": {
                "childs": [
                    {"name": "Patched Child 1", "age": 11},
                    {"name": "Patched Child 2", "age": 16},
                    {"name": "New Child 3", "age": 20}
                ],
                "qs_field": [self.relation1.pk]  # Required field
            }
        }
        
        response = self.client.patch(f"/api/testmodels/{self.test_model.pk}/", patch_data, format="json")
        assert response.status_code == 200
        
        # Verify the nested list was updated correctly
        self.test_model.refresh_from_db()
        assert len(self.test_model.structured_data.childs) == 3
        assert self.test_model.structured_data.childs[0].name == "Patched Child 1"
        assert self.test_model.structured_data.childs[1].name == "Patched Child 2"
        assert self.test_model.structured_data.childs[2].name == "New Child 3"
    
    def test_patch_foreign_key(self):
        """Test patching a foreign key field within structured data"""
        patch_data = {
            "structured_data": {
                "fk_field": self.relation2.pk,
                "qs_field": [self.relation1.pk]  # Required field
            }
        }
        
        response = self.client.patch(f"/api/testmodels/{self.test_model.pk}/", patch_data, format="json")
        assert response.status_code == 200
        
        # Verify the foreign key was updated correctly
        self.test_model.refresh_from_db()
        assert self.test_model.structured_data.fk_field.pk == self.relation2.pk
    
    def test_patch_queryset_field(self):
        """Test patching a queryset field within structured data"""
        patch_data = {
            "structured_data": {
                "qs_field": [self.relation1.pk, self.relation2.pk]
                # No need to add qs_field separately as we're already updating it
            }
        }
        
        response = self.client.patch(f"/api/testmodels/{self.test_model.pk}/", patch_data, format="json")
        assert response.status_code == 200
        
        # Verify the queryset field was updated correctly
        self.test_model.refresh_from_db()
        assert len(self.test_model.structured_data.qs_field) == 2
        assert self.relation1.pk in [obj.pk for obj in self.test_model.structured_data.qs_field]
        assert self.relation2.pk in [obj.pk for obj in self.test_model.structured_data.qs_field]

    def test_union_schema_field(self):
        """Test creating, retrieving, and updating a model with union schema in structured_data_union"""
        # Create with TestSchema
        create_data = {
            "title": "Union Model",
            "structured_data": {
                "type": "schema1",
                "name": "Union Name",
                "age": 22,
                "qs_field": [self.relation1.pk],
                "fk_field": self.relation1.pk
            },
            "structured_data_union": {
                "data": {
                    "type": "schema1",
                    "name": "Union TestSchema",
                    "age": 50,
                    "qs_field": [self.relation1.pk],
                    "fk_field": self.relation1.pk
                }
            }
        }
        response = self.client.post("/api/testmodels/", create_data, format="json")
        assert response.status_code == 201
        created_id = response.json()["id"]
        # Retrieve and check
        response = self.client.get(f"/api/testmodels/{created_id}/")
        assert response.status_code == 200
        data = response.json()
        assert data["structured_data_union"]["data"]["name"] == "Union TestSchema"
        assert data["structured_data_union"]["data"]["age"] == 50
        # Update with TestSchema2
        update_data = {
            "title": "Union Model Updated",
            "structured_data_union": {
                "data": {
                    "type": "schema2",
                    "name_2": "Union TestSchema2",
                    "age_2": 60,
                    "qs_field_2": [self.relation2.pk],
                    "fk_field_2": self.relation2.pk
                }
            }
        }
        response = self.client.patch(f"/api/testmodels/{created_id}/", update_data, format="json")
        assert response.status_code == 200
        # Retrieve and check updated
        response = self.client.get(f"/api/testmodels/{created_id}/")
        assert response.status_code == 200
        data = response.json()
        assert data["structured_data_union"]["data"]["name_2"] == "Union TestSchema2"
        assert data["structured_data_union"]["data"]["age_2"] == 60

