import block from 'bem-css-modules';
import { Formik } from 'formik';
import { AvailabilityRow } from '@features/pages/main/availability';
import { Rating } from '@features/pages/main/rating';
import { Checkbox } from '@ui/checkbox';
import style from './form_filter.module.sass';
import { useContext, useRef } from 'react';
import { MapContext } from '@ui/map/map.context';

const b = block(style);


export const useMap = () => {
  return useContext(MapContext);
};
export function FormFilter(): JSX.Element {

  const map = useMap(); // Получаем экземпляр карты
  
  console.log('Состояние карты:', {
      isStyleLoaded: map?.isStyleLoaded(),
      loaded: map?.loaded(),
      style: map?.getStyle()})
  const handleCheckboxChange = (layerId: string, isChecked: boolean) => {
    if (map) {
      console.log(isChecked.toString())
      const visibility = isChecked ? 'visible' : 'none';
      map.setLayoutProperty(layerId, 'visibility', visibility);
      
    }
  };

  return (
    <div className={b({ filter: true })}>
      <Formik initialValues={{ test: false }} validationSchema={{}} onSubmit={console.log}>
        {() => (
          <>
            <div>
              <Checkbox 
                defaultChecked={false}
                onChange={(isChecked:boolean) => handleCheckboxChange('infrastructure_near', isChecked)}
              >
                <Rating
                  desc={'Доступность социальной инфраструктуры'}
                  name={'name_1'}
                  ranges={[1, 2, 3, 4, 5]}
                />
              </Checkbox>
            </div>
            <div>
              <Checkbox 
                defaultChecked={false}
                
                onChange={(e) => handleCheckboxChange('population-density-layer', e)}
              >
                <Rating
                  desc={'Плотность населения'}
                  name={'name_2'}
                  ranges={[1, 2, 3, 4, 5]}
                />
              </Checkbox>
            </div>
            <div>
              <Checkbox 
                defaultChecked={false}
                onChange={(e) => handleCheckboxChange('building-density-layer', e)}
              >
                <Rating 
                  desc={'Плотность застройки'} 
                  name={'name_3'} 
                  ranges={[1, 2, 3, 4, 5]} />
              </Checkbox>
            </div>  
            <div>
              <Checkbox 
                defaultChecked={false}
                onChange={(e) => handleCheckboxChange('schools-layer',e)}
              >
                <AvailabilityRow destination={'школы'} />
              </Checkbox>
            </div>
            <div>
              <Checkbox 
                defaultChecked={false}
                onChange={(e) => handleCheckboxChange('default-layer', e)}
              >
                <AvailabilityRow />
              </Checkbox>
            </div>
            <div>
              <button>Добавить условие</button>
              <button>Сбросить</button>
            </div>
          </>
        )}
      </Formik>
    </div>
  )
}