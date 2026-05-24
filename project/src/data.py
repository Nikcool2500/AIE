from pydantic import BaseModel, Field
from typing import Literal

GenderType = Literal["M", "F", "Unknown"]

EducationLevelType = Literal[
    "High School", 
    "Graduate", 
    "Uneducated", 
    "College", 
    "Post-Graduate", 
    "Doctorate",
    "Unknown", 
]

MaritalStatusType = Literal[
    "Married", 
    "Single", 
    "Divorced",
    "Unknown", 
]

IncomeCategoryType = Literal[
    "Less than $40K", 
    "$60K - $80K", 
    "$80K - $120K", 
    "$40K - $60K", 
    "$120K +", 
    "Unknown"
]

CardCategoryType = Literal[
    "Blue", 
    "Gold", 
    "Silver", 
    "Platinum",
    "Unknown", 
]

class ClientProfile(BaseModel):
    """
    Схема данных клиента для прогноза кредитного лимита.
    Использует Literal для ограничения ввода только допустимыми категориями.
    """
    Customer_Age: int = Field(..., ge=18, le=100, example=35, description="Возраст клиента (18-100)")
    Gender: GenderType = Field(..., example="M", description="Пол")
    Dependent_count: int = Field(..., ge=0, le=10, example=2, description="Количество иждивенцев")
    Education_Level: EducationLevelType = Field(..., example="Graduate", description="Уровень образования")
    Marital_Status: MaritalStatusType = Field(..., example="Married", description="Семейное положение")
    Income_Category: IncomeCategoryType = Field(..., example="$60K - $80K", description="Категория дохода")
    Card_Category: CardCategoryType = Field(..., example="Blue", description="Тип карты")
    
    Months_on_book: int = Field(..., ge=13, le=56, example=39, description="Месяцев обслуживания в банке")
    Total_Relationship_Count: int = Field(..., ge=1, le=6, example=5, description="Количество продуктов банка")
    Months_Inactive_12_mon: int = Field(..., ge=0, le=6, example=1, description="Месяцев неактивности")
    Contacts_Count_12_mon: int = Field(..., ge=0, le=6, example=3, description="Контактов с поддержкой")
    
    Credit_Limit: float = Field(..., gt=0, example=10000.0, description="Текущий лимит")
    Total_Revolving_Bal: int = Field(..., ge=0, example=777, description="Оборотный баланс")
    Total_Amt_Chng_Q4_Q1: float = Field(..., example=0.75, description="Изменение суммы транзакций Q4/Q1")
    Total_Trans_Amt: int = Field(..., ge=0, example=4400, description="Сумма транзакций")
    Total_Trans_Ct: int = Field(..., ge=0, example=65, description="Количество транзакций")
    Total_Ct_Chng_Q4_Q1: float = Field(..., example=0.7, description="Изменение кол-ва транзакций Q4/Q1")
    Avg_Utilization_Ratio: float = Field(..., ge=0, le=1, example=0.3, description="Коэффициент использования лимита")

class PredictionResponse(BaseModel):
    predicted_credit_limit: float
    status: str = "success"